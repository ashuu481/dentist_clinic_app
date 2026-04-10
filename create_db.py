<<<<<<< HEAD
import sqlite3

conn = sqlite3.connect('database.db')

# Patients table (already exists)
conn.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    mobile TEXT,
    age TEXT,
    gender TEXT,
    complaint TEXT
)
""")

# NEW: Treatments table
conn.execute("""
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

conn.commit()
conn.close()

=======
import sqlite3

conn = sqlite3.connect('database.db')

# Patients table (already exists)
conn.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    mobile TEXT,
    age TEXT,
    gender TEXT,
    complaint TEXT
)
""")

# NEW: Treatments table
conn.execute("""
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

conn.commit()
conn.close()

>>>>>>> bfcd717e0d42a8372cf9a6604f24cb84bd0751c4
print("Database updated!")