from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import mysql.connector
from werkzeug.security import check_password_hash
from functools import wraps
import csv
import io

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

DB_CONFIG = {
    "host": "gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com",
    "port": 4000,
    "user": "3p4oDGx2vdiHDMg.root",
    "password": "Wi65W1a6rIl8q5qL",
    "database": "volunteer_db",
    "autocommit": True,
    "use_pure": True,
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("admin_login"))
        return func(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        age = request.form.get("age")
        gender = request.form.get("gender")
        address = request.form.get("address")
        skills = request.form.get("skills")
        availability = request.form.get("availability")
        interest_area = request.form.get("interest_area")

        if not name or not email or not phone or not age:
            flash("Name, email, phone and age are required.", "error")
            return redirect(url_for("register"))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = '''
                INSERT INTO volunteers
                (name, email, phone, age, gender, address, skills, availability, interest_area)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            values = (name, email, phone, age, gender, address, skills, availability, interest_area)
            cursor.execute(query, values)
            conn.commit()
            flash("Registration successful! Your application is pending approval.", "success")
            return redirect(url_for("home"))

        except mysql.connector.IntegrityError:
            flash("This email is already registered.", "error")
            return redirect(url_for("register"))

        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()

        cursor.close()
        conn.close()

        if admin and check_password_hash(admin["password"], password):
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")

@app.route("/admin/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM volunteers")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS pending FROM volunteers WHERE status = 'Pending'")
    pending = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) AS approved FROM volunteers WHERE status = 'Approved'")
    approved = cursor.fetchone()["approved"]

    cursor.execute("SELECT COUNT(*) AS rejected FROM volunteers WHERE status = 'Rejected'")
    rejected = cursor.fetchone()["rejected"]

    cursor.execute("SELECT * FROM volunteers ORDER BY registered_at DESC LIMIT 5")
    recent_volunteers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected,
        recent_volunteers=recent_volunteers
    )

@app.route("/admin/volunteers")
@login_required
def volunteers():
    status = request.args.get("status")
    search = request.args.get("search")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM volunteers WHERE 1=1"
    values = []

    if status:
        query += " AND status = %s"
        values.append(status)

    if search:
        query += " AND (name LIKE %s OR email LIKE %s OR phone LIKE %s)"
        search_value = f"%{search}%"
        values.extend([search_value, search_value, search_value])

    query += " ORDER BY registered_at DESC"

    cursor.execute(query, values)
    all_volunteers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("volunteers.html", volunteers=all_volunteers, status=status, search=search)

@app.route("/admin/update-status/<int:volunteer_id>", methods=["POST"])
@login_required
def update_status(volunteer_id):
    new_status = request.form.get("status")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE volunteers SET status = %s WHERE id = %s",
        (new_status, volunteer_id)
    )
    conn.commit()

    cursor.close()
    conn.close()

    flash("Volunteer status updated.", "success")
    return redirect(url_for("volunteers"))

@app.route("/admin/delete/<int:volunteer_id>", methods=["POST"])
@login_required
def delete_volunteer(volunteer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM volunteers WHERE id = %s", (volunteer_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Volunteer deleted successfully.", "success")
    return redirect(url_for("volunteers"))

@app.route("/admin/report")
@login_required
def generate_report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM volunteers ORDER BY registered_at DESC")
    volunteers = cursor.fetchall()

    cursor.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Name", "Email", "Phone", "Age", "Gender",
        "Address", "Skills", "Availability", "Interest Area",
        "Status", "Registered At"
    ])

    for volunteer in volunteers:
        writer.writerow([
            volunteer["id"],
            volunteer["name"],
            volunteer["email"],
            volunteer["phone"],
            volunteer["age"],
            volunteer["gender"],
            volunteer["address"],
            volunteer["skills"],
            volunteer["availability"],
            volunteer["interest_area"],
            volunteer["status"],
            volunteer["registered_at"]
        ])

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=volunteer_report.csv"
    return response

if __name__ == "__main__":
    app.run(debug=True)
