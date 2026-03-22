from flask import Flask, render_template, request, redirect, url_for, session
from web.db import init_db, get_user_by_id
from web.auth import register, login

app = Flask(__name__)
app.secret_key = __import__("os").getenv("SECRET_KEY", "dev")

@app.before_request
def load_user():
    request.user = None
    if "user_id" in session:
        request.user = get_user_by_id(session["user_id"])

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.user:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user_id, error = register(email, password)
        if error:
            return render_template("register.html", error=error)
        session["user_id"] = user_id
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user_id, error = login(email, password)
        if error:
            return render_template("login.html", error=error)
        session["user_id"] = user_id
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", user=request.user)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
