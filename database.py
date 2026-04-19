import sqlite3
import hashlib

conn = sqlite3.connect("app.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    topic TEXT,
    score INTEGER
)
""")

conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    try:
        cursor.execute(
            "INSERT INTO users VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    return cursor.fetchone()

def save_score(username, topic, score):
    cursor.execute(
        "INSERT INTO history (username, topic, score) VALUES (?, ?, ?)",
        (username, topic, score)
    )
    conn.commit()

def get_history(username):
    cursor.execute(
        "SELECT topic, score FROM history WHERE username=?",
        (username,)
    )
    return cursor.fetchall()