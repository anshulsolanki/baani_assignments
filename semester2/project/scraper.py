import csv
import requests
import mysql.connector
from pymongo import MongoClient
import base64
import os

# Database configurations
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "arena")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "arena")

def get_db_connections():
    mysql_conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DATABASE]
    return mysql_conn, mongo_client, mongo_db

def run_scraper():
    print("Starting scraper pipeline...")
    
    try:
        mysql_conn, mongo_client, mongo_db = get_db_connections()
        mysql_cursor = mysql_conn.cursor()
    except Exception as e:
        print(f"Failed to connect to databases: {e}")
        return

    csv_file = "batch_data.csv"
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            uid = row['uid']
            name = row['name']
            website_url = row['website_url']
            
            image_url = f"{website_url}/images/pfp.jpg"
            print(f"Processing {uid} ({name}) -> {image_url}")
            
            try:
                response = requests.get(image_url, timeout=5)
                
                if response.status_code == 200:
                    print(f"  Success: Image fetched for {uid}")
                    image_data = response.content
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    # 1. Insert/Update MySQL
                    try:
                        mysql_cursor.execute("""
                            INSERT INTO users (uid, name)
                            VALUES (%s, %s)
                            ON DUPLICATE KEY UPDATE name = VALUES(name)
                        """, (uid, name))
                        mysql_conn.commit()
                        print(f"  MySQL updated for {uid}")
                    except mysql.connector.Error as err:
                        print(f"  MySQL Error for {uid}: {err}")
                        
                    # 2. Upsert MongoDB
                    try:
                        mongo_db.profile_images.update_one(
                            {"uid": uid},
                            {"$set": {"image_data": image_base64}},
                            upsert=True
                        )
                        print(f"  MongoDB updated for {uid}")
                    except Exception as e:
                        print(f"  MongoDB Error for {uid}: {e}")
                        
                elif response.status_code == 404:
                    print(f"  Warning: Image not found (404) for {uid}")
                else:
                    print(f"  Warning: HTTP {response.status_code} for {uid}")
                    
            except requests.exceptions.Timeout:
                print(f"  Error: Timeout for {uid}")
            except requests.exceptions.RequestException as e:
                print(f"  Error: Request failed for {uid}: {e}")
            except Exception as e:
                print(f"  Unexpected error for {uid}: {e}")

    mysql_cursor.close()
    mysql_conn.close()
    mongo_client.close()
    print("Scraper pipeline finished.")

if __name__ == "__main__":
    run_scraper()
