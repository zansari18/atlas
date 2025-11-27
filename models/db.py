import sqlite3 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
DB_FILE = "database.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
         CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            last_updated TEXT
        );
    """)
    conn.commit()
def create_user(username, password):
    conn = get_db()
    cursor = conn.cursor()

    pw_hash = generate_password_hash(password)

    cursor.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
    conn.commit()

def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()

def update_location(user_id, lat, lon):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET latitude = ?, longitude = ?, last_updated = ?
        WHERE id = ?
    """, (lat, lon, datetime.utcnow().isoformat(), user_id))
    conn.commit()
def get_locations():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT username, latitude, longitude FROM users")
    return cursor.fetchall()
    
                   