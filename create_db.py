import sqlite3
import os

DB_PATH = "database.db"

def init():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        gender TEXT,
        mobile TEXT,
        complaint TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        treatment TEXT,
        description TEXT,
        date TEXT,
        next_visit TEXT,
        cost REAL
    )
    """)

    # default admin
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users(username,password,role) VALUES (?,?,?)",
                  ("admin", "admin", "doctor"))

    conn.commit()
    conn.close()
    print("DB Ready")

if __name__ == "__main__":
    init()