from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import mysql.connector
from pymongo import MongoClient
import os
import base64
import json
import math
from facial_recognition_module import find_closest_match

app = FastAPI()

# Database configurations
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "arena")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "arena")

# Helper to get DB connections
def get_mysql_conn():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

def get_mongo_db():
    client = MongoClient(MONGO_URI)
    return client[MONGO_DATABASE]

# Pydantic models
class LoginRequest(BaseModel):
    image_data: str # Base64 encoded image

# In-memory session storage (for simplicity in this assignment)
# In production, use Redis or a secure database
sessions = {}

@app.post("/api/login")
async def login(request: LoginRequest):
    image_data = request.image_data
    
    # 1. Fetch all stored profile images from MongoDB
    mongo_db = get_mongo_db()
    cursor = mongo_db.profile_images.find({}, {"uid": 1, "image_data": 1})
    db_images_dict = {}
    for doc in cursor:
        db_images_dict[doc["uid"]] = doc["image_data"]
        
    if not db_images_dict:
        raise HTTPException(status_code=400, detail="No profile images found in database.")
        
    # 2. Call facial recognition
    matched_uid = find_closest_match(image_data, db_images_dict)
    
    if not matched_uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Facial verification failed.")
        
    # 3. Cross-reference with MySQL
    mysql_conn = get_mysql_conn()
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE uid = %s", (matched_uid,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        mysql_conn.close()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found in metadata database.")
        
    # 4. Set user's is_online flag to TRUE
    cursor.execute("UPDATE users SET is_online = TRUE WHERE uid = %s", (matched_uid,))
    mysql_conn.commit()
    
    cursor.close()
    mysql_conn.close()
    
    # 5. Establish session (dummy session for now)
    session_id = f"sess_{matched_uid}"
    sessions[session_id] = matched_uid
    
    response = JSONResponse(content={"message": "Login successful", "uid": matched_uid, "name": user["name"]})
    response.set_cookie(key="session_id", value=session_id)
    return response

@app.post("/api/logout")
async def logout(uid: str):
    # Set user's is_online flag to FALSE
    mysql_conn = get_mysql_conn()
    cursor = mysql_conn.cursor()
    cursor.execute("UPDATE users SET is_online = FALSE WHERE uid = %s", (uid,))
    mysql_conn.commit()
    cursor.close()
    mysql_conn.close()
    return {"message": "Logged out"}
# --- Phase 3 & 4 Logic ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, uid: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[uid] = websocket
        await self.broadcast_lobby_update()

    async def disconnect(self, uid: str):
        if uid in self.active_connections:
            del self.active_connections[uid]
            await self.broadcast_lobby_update()

    async def broadcast_lobby_update(self):
        # Fetch online users from MySQL
        mysql_conn = get_mysql_conn()
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT uid, name, elo_rating FROM users WHERE is_online = TRUE")
        online_users = cursor.fetchall()
        cursor.close()
        mysql_conn.close()

        message = json.dumps({
            "type": "lobby_update",
            "users": online_users
        })
        
        for connection in self.active_connections.values():
            await connection.send_text(message)

    async def send_personal_message(self, message: str, uid: str):
        if uid in self.active_connections:
            await self.active_connections[uid].send_text(message)

manager = ConnectionManager()
active_games = {}

def calculate_elo(r_player, r_opponent, s_player):
    k = 32
    e_player = 1 / (1 + 10**((r_opponent - r_player) / 400))
    return round(r_player + k * (s_player - e_player))

@app.websocket("/ws/arena/{uid}")
async def websocket_arena(websocket: WebSocket, uid: str):
    await manager.connect(uid, websocket)
    
    # Set user online in DB just in case (Phase 2 should have done it)
    mysql_conn = get_mysql_conn()
    cursor = mysql_conn.cursor()
    cursor.execute("UPDATE users SET is_online = TRUE WHERE uid = %s", (uid,))
    mysql_conn.commit()
    cursor.close()
    mysql_conn.close()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "send_challenge":
                target_uid = message["target_uid"]
                # Fetch challenger name
                mysql_conn = get_mysql_conn()
                cursor = mysql_conn.cursor(dictionary=True)
                cursor.execute("SELECT name FROM users WHERE uid = %s", (uid,))
                challenger = cursor.fetchone()
                cursor.close()
                mysql_conn.close()
                
                await manager.send_personal_message(json.dumps({
                    "type": "challenge_received",
                    "from_uid": uid,
                    "from_name": challenger["name"] if challenger else "Unknown"
                }), target_uid)
                
            elif message["type"] == "decline_challenge":
                challenger_uid = message["challenger_uid"]
                # Fetch decliner name
                mysql_conn = get_mysql_conn()
                cursor = mysql_conn.cursor(dictionary=True)
                cursor.execute("SELECT name FROM users WHERE uid = %s", (uid,))
                decliner = cursor.fetchone()
                cursor.close()
                mysql_conn.close()
                
                await manager.send_personal_message(json.dumps({
                    "type": "challenge_rejected",
                    "by_uid": uid,
                    "by_name": decliner["name"] if decliner else "Unknown"
                }), challenger_uid)
                
            elif message["type"] == "accept_challenge":
                challenger_uid = message["challenger_uid"]
                room_id = f"room_{challenger_uid}_{uid}"
                
                active_games[room_id] = {
                    "players": [challenger_uid, uid],
                    "board": [None] * 9,
                    "turn": challenger_uid, # Challenger goes first (X)
                    "symbols": {challenger_uid: 'X', uid: 'O'}
                }
                
                # Notify both players
                await manager.send_personal_message(json.dumps({
                    "type": "game_start",
                    "room_id": room_id,
                    "symbol": 'X',
                    "opponent": uid
                }), challenger_uid)
                
                await manager.send_personal_message(json.dumps({
                    "type": "game_start",
                    "room_id": room_id,
                    "symbol": 'O',
                    "opponent": challenger_uid
                }), uid)
                
            elif message["type"] == "make_move":
                room_id = message["room_id"]
                idx = message["index"]
                
                if room_id in active_games:
                    game = active_games[room_id]
                    if game["turn"] == uid and 0 <= idx < 9 and game["board"][idx] is None:
                        symbol = game["symbols"][uid]
                        game["board"][idx] = symbol
                        
                        # Check for winner
                        winner = check_winner(game["board"])
                        
                        # Switch turn
                        next_turn = [p for p in game["players"] if p != uid][0]
                        game["turn"] = next_turn
                        
                        # Broadcast update
                        update_msg = json.dumps({
                            "type": "game_update",
                            "board": game["board"],
                            "turn": game["symbols"][next_turn],
                            "winner": symbol if winner else ("Draw" if all(c is not None for c in game["board"]) else None)
                        })
                        
                        for p_uid in game["players"]:
                            await manager.send_personal_message(update_msg, p_uid)
                            
                        if winner or all(c is not None for c in game["board"]):
                            # #TODO: Verification point - Verify Elo update logic in tests
                            await resolve_game(room_id, symbol if winner else None)
                            
    except WebSocketDisconnect:
        print(f"Client {uid} disconnected")
        await manager.disconnect(uid)
        
        # Handle mid-game disconnect (Phase 4)
        for room_id, game in list(active_games.items()):
            if uid in game["players"]:
                opponent_uid = [p for p in game["players"] if p != uid][0]
                await manager.send_personal_message(json.dumps({
                    "type": "opponent_disconnected"
                }), opponent_uid)
                
                # #TODO: Verification point - Verify forfeit Elo update in tests
                await resolve_game(room_id, opponent_uid, forfeit=True)

def check_winner(board):
    win_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Cols
        [0, 4, 8], [2, 4, 6]             # Diags
    ]
    for p in win_patterns:
        if board[p[0]] and board[p[0]] == board[p[1]] == board[p[2]]:
            return True
    return False

async def resolve_game(room_id, winner_symbol_or_uid, forfeit=False):
    if room_id not in active_games:
        return
        
    game = active_games[room_id]
    p1, p2 = game["players"]
    
    # Fetch current ratings
    mysql_conn = get_mysql_conn()
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT uid, elo_rating FROM users WHERE uid IN (%s, %s)", (p1, p2))
    users = cursor.fetchall()
    
    ratings = {u["uid"]: u["elo_rating"] for u in users}
    
    r1 = ratings.get(p1, 1200)
    r2 = ratings.get(p2, 1200)
    
    s1, s2 = 0.5, 0.5 # Default draw
    
    if forfeit:
        # winner_symbol_or_uid is the UID of the winner
        if p1 == winner_symbol_or_uid:
            s1, s2 = 1.0, 0.0
        else:
            s1, s2 = 0.0, 1.0
    elif winner_symbol_or_uid:
        # winner_symbol_or_uid is 'X' or 'O'
        p1_symbol = game["symbols"][p1]
        if p1_symbol == winner_symbol_or_uid:
            s1, s2 = 1.0, 0.0
        else:
            s1, s2 = 0.0, 1.0
            
    new_r1 = calculate_elo(r1, r2, s1)
    new_r2 = calculate_elo(r2, r1, s2)
    
    # Update DB
    # #TODO: Verification point - Verify DB update works correctly
    cursor.execute("UPDATE users SET elo_rating = %s WHERE uid = %s", (new_r1, p1))
    cursor.execute("UPDATE users SET elo_rating = %s WHERE uid = %s", (new_r2, p2))
    mysql_conn.commit()
    cursor.close()
    mysql_conn.close()
    
    # Remove game
    del active_games[room_id]

@app.get("/api/leaderboard")
async def get_leaderboard():
    # #TODO: Verification point - Verify leaderboard returns correct order
    mysql_conn = get_mysql_conn()
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT uid, name, elo_rating FROM users ORDER BY elo_rating DESC")
    leaderboard = cursor.fetchall()
    cursor.close()
    mysql_conn.close()
    return leaderboard


# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
