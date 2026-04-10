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
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'doctor'
    )
    """)

    # ---------------- PATIENTS TABLE ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
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

    # ---------------- APPOINTMENTS TABLE ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        doctor_name TEXT,
        date TEXT,
        time TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    # ---------------- BILLS TABLE ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        amount REAL,
        description TEXT,
        date TEXT
    )
    """)

    # ---------------- REMINDERS TABLE ----------------
    c.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        message TEXT,
        date TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    # ---------------- DEFAULT ADMIN ----------------
    c.execute("SELECT * FROM users WHERE username=?", ("admin",))
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