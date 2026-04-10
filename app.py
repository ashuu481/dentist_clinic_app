from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3, os
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "clinic_secret"

DB = "database.db"

# ---------- DB ----------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- HOME ----------
@app.route("/")
def home():
    return redirect("/login")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p)).fetchone()
        conn.close()

        if user:
            session["user"] = u
            return redirect("/dashboard")

        return "Invalid Login"

    return render_template("login.html")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    treatments = conn.execute("SELECT COUNT(*) FROM treatments").fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           total_patients=patients,
                           total_treatments=treatments)

# ---------- PATIENTS ----------
@app.route("/patients", methods=["GET","POST"])
def patients():
    if "user" not in session:
        return redirect("/login")

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

    data = conn.execute("SELECT * FROM patients").fetchall()
    conn.close()

    return render_template("patients.html", patients=data)

# ---------- TREATMENT ----------
@app.route("/treatment/<int:id>", methods=["GET","POST"])
def treatment(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        INSERT INTO treatments(patient_id,treatment,description,date,next_visit,cost)
        VALUES (?,?,?,?,?,?)
        """, (
            id,
            request.form["treatment"],
            request.form["description"],
            request.form["date"],
            request.form["next_visit"],
            request.form["cost"]
        ))
        conn.commit()

    data = conn.execute("SELECT * FROM treatments WHERE patient_id=?", (id,)).fetchall()
    conn.close()

    return render_template("treatment.html", treatments=data, patient_id=id)

# ---------- REPORT ----------
@app.route("/report/<int:id>")
def report(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    patient = conn.execute("SELECT * FROM patients WHERE id=?", (id,)).fetchone()
    treatments = conn.execute("SELECT * FROM treatments WHERE patient_id=?", (id,)).fetchall()

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

# ---------- REMINDERS ----------
@app.route("/reminders")
def reminders():
    if "user" not in session:
        return redirect("/login")

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

# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)