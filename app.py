import os
import sqlite3
from datetime import date

from flask import Flask, render_template, request, redirect, session, send_file

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ================= APP =================
app = Flask(__name__)
app.secret_key = "super_secret_key_123"

DB_NAME = "database.db"

# ================= DB =================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ================= INIT DB SAFE =================
def init_db():
    conn = get_db()
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
        cost REAL,
        date TEXT,
        next_visit TEXT
    )
    """)

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

    c.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        amount REAL,
        description TEXT,
        date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        mobile TEXT,
        message TEXT,
        date TEXT
    )
    """)

    # default admin
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users(username,password,role) VALUES (?,?,?)",
            ("admin", "admin", "doctor")
        )

    conn.commit()
    conn.close()


init_db()


# ================= REMINDER SYSTEM =================
def send_reminder(name, mobile, message):
    print("📩 REMINDER SENT")
    print("To:", name, mobile)
    print("Message:", message)
@app.route("/test")
def test():
    return "Flask is working"

# ================= HOME =================
@app.route("/")
def home():
    return redirect("/login")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, p)
        ).fetchone()
        conn.close()

        if user:
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    treatments = conn.execute("SELECT COUNT(*) FROM treatments").fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_patients=patients,
        total_treatments=treatments
    )


# ================= PATIENTS (SEARCH + ADD) =================
@app.route("/patients", methods=["GET", "POST"])
def patients():
    if "user" not in session:
        return redirect("/login")

    q = request.args.get("q")

    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        INSERT INTO patients(name,age,gender,mobile,complaint)
        VALUES (?,?,?,?,?)
        """, (
            request.form["name"],
            request.form["age"],
            request.form["gender"],
            request.form["mobile"],
            request.form["complaint"]
        ))
        conn.commit()

    if q:
        data = conn.execute(
            "SELECT * FROM patients WHERE name LIKE ?",
            ("%"+q+"%",)
        ).fetchall()
    else:
        data = conn.execute("SELECT * FROM patients").fetchall()

    conn.close()

    return render_template("patients.html", patients=data)


# ================= APPOINTMENTS =================
@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        INSERT INTO appointments(patient_name,doctor_name,date,time)
        VALUES (?,?,?,?)
        """, (
            request.form["patient"],
            request.form["doctor"],
            request.form["date"],
            request.form["time"]
        ))
        conn.commit()

    data = conn.execute("SELECT * FROM appointments").fetchall()
    conn.close()

    return render_template("appointments.html", appts=data)


# ================= BILLING =================
@app.route("/billing", methods=["GET", "POST"])
def billing():
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        INSERT INTO bills(patient_name,amount,description,date)
        VALUES (?,?,?,?)
        """, (
            request.form["patient"],
            request.form["amount"],
            request.form["desc"],
            request.form["date"]
        ))
        conn.commit()

    bills = conn.execute("SELECT * FROM bills").fetchall()
    conn.close()

    return render_template("billing.html", bills=bills)


# ================= TREATMENT =================
@app.route("/treatment/<int:id>", methods=["GET", "POST"])
def treatment(id):
    conn = get_db()

    # ✅ Get patient
    patient = conn.execute(
        "SELECT * FROM patients WHERE id=?",
        (id,)
    ).fetchone()

    if not patient:
        conn.close()
        return "Patient Not Found", 404

    # ✅ Save treatment
    if request.method == "POST":
        conn.execute("""
        INSERT INTO treatments(patient_id, treatment, description, cost, date, next_visit)
        VALUES (?,?,?,?,?,?)
        """, (
            id,
            request.form.get("treatment"),
            request.form.get("description"),
            request.form.get("cost") or 0,
            request.form.get("date"),
            request.form.get("next_visit")
        ))
        conn.commit()

    # ✅ Fetch treatments
    treatments = conn.execute(
        "SELECT * FROM treatments WHERE patient_id=?",
        (id,)
    ).fetchall()

    conn.close()

    return render_template(
        "treatments.html",
        patient=patient,
        treatments=treatments,
        patient_id=id
    )

# ================= REPORT (PDF) =================
@app.route("/report/<int:id>")
def report(id):
    conn = get_db()

    patient = conn.execute(
        "SELECT * FROM patients WHERE id=?",
        (id,)
    ).fetchone()

    treatments = conn.execute(
        "SELECT * FROM treatments WHERE patient_id=?",
        (id,)
    ).fetchall()

    conn.close()

    file = f"report_{id}.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("Clinic Report", styles["Title"]))
    content.append(Paragraph(f"Patient: {patient['name']}", styles["Normal"]))

    total = 0
    for t in treatments:
        cost = float(t["cost"] or 0)
        total += cost
        content.append(Paragraph(f"{t['treatment']} - ₹{cost}", styles["Normal"]))

    content.append(Paragraph(f"TOTAL: ₹{total}", styles["Title"]))

    doc.build(content)

    return send_file(file, as_attachment=True)


# ================= REMINDERS =================
@app.route("/reminders")
def reminders():
    conn = get_db()
    today = date.today().isoformat()

    data = conn.execute("""
    SELECT patients.name, patients.mobile, treatments.next_visit
    FROM treatments
    JOIN patients ON patients.id = treatments.patient_id
    WHERE next_visit <= ?
    """, (today,)).fetchall()

    conn.close()

    return render_template("reminders.html", patients=data)


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)