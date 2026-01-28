from flask import Flask, render_template, request, redirect, url_for, session
from db import get_connection

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()
        except:
            return render_template("register.html", error="Username already exists")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("questions"))
        else:
            return render_template("index.html", error="Invalid credentials")

    return render_template("index.html")


# ---------- CONSULTATION ----------
@app.route("/questions", methods=["GET", "POST"])
def questions():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        symptoms = ", ".join(request.form.getlist("symptoms"))
        severity = request.form["severity"]
        days = request.form["days"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO patients (username, name, age, symptoms, severity, days)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session["username"], name, age, symptoms, severity, days))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("result"))

    return render_template("questions.html")


# ---------- RESULT ----------
@app.route("/result")
def result():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM patients WHERE username=%s ORDER BY id DESC LIMIT 1",
        (session["username"],)
    )
    data = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("result.html", data=data)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
