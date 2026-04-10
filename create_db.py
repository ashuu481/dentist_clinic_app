import sqlite3

DB_NAME = "database.db"

def create_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_tables():
    conn = create_connection()
    c = conn.cursor()

    # ---------------- USERS TABLE ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'doctor'
    )
    """)

    # ---------------- PATIENTS TABLE ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age TEXT,
        gender TEXT,
        mobile TEXT,
        address TEXT,
        complaint TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------- TREATMENTS TABLE ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        treatment TEXT,
        description TEXT,
        cost REAL,
        date TEXT,
        next_visit TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    # ---------------- REMINDERS TABLE ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        message TEXT,
        reminder_date TEXT,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    # ---------------- DEFAULT ADMIN USER ----------------
    c.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    admin = c.fetchone()

    if not admin:
        c.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, ("admin", "admin", "doctor"))

    conn.commit()
    conn.close()
    print("✅ Database created successfully!")


if __name__ == "__main__":
    create_tables()