import mysql.connector
from pymongo import MongoClient
import os

# Database configurations (can be overridden by environment variables)
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "arena")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "arena")

def setup_mysql():
    print("Setting up MySQL...")
    try:
        # Connect without database to create it if it doesn't exist
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        conn.commit()
        cursor.close()
        conn.close()

        # Connect to the database
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                elo_rating INT DEFAULT 1200,
                is_online BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        print("MySQL setup completed successfully.")
        
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def setup_mongo():
    print("Setting up MongoDB...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DATABASE]
        
        # MongoDB creates collections lazily, but we can insert a dummy doc and delete it
        # or just list collections to make sure we can connect.
        
        # Check connection
        client.server_info()
        print("MongoDB connected successfully.")
        
        # We will use collection 'profile_images'
        # No explicit creation needed usually, but we can create an index on uid
        db.profile_images.create_index("uid", unique=True)
        print("MongoDB setup completed successfully (Index created).")
        
    except Exception as e:
        print(f"MongoDB Error: {e}")

if __name__ == "__main__":
    setup_mysql()
    setup_mongo()
