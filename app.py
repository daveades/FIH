import os
import threading
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request, redirect, url_for, session

load_dotenv()
from web.db import init_db, get_user_by_id, update_user_keys, get_all_users
from web.auth import register, login

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

KEY_FIELDS = ["anthropic_api_key", "notion_api_key", "alpha_vantage_api_key"]
DB_ID_FIELDS = ["watchlist_db_id", "research_notes_db_id", "earnings_calendar_db_id", "daily_digest_db_id"]

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

def keys_configured(user):
    return all(user.get(k) for k in KEY_FIELDS + DB_ID_FIELDS)

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
    return render_template("dashboard.html", user=request.user, keys_ok=keys_configured(request.user))

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    saved = False
    if request.method == "POST":
        keys = {k: request.form.get(k, "").strip() for k in KEY_FIELDS}
        # don't overwrite existing keys if the field was left blank
        existing = {k: request.user[k] for k in KEY_FIELDS}
        merged = {k: keys[k] if keys[k] else existing[k] for k in KEY_FIELDS}
        update_user_keys(request.user["id"], merged)
        request.user = get_user_by_id(request.user["id"])
        saved = True
    return render_template("settings.html", user=request.user, saved=saved)

@app.route("/setup-notion", methods=["POST"])
@login_required
def setup_notion():
    from flask import jsonify
    from tools.notion_setup import setup_notion_workspace
    api_key = request.user.get("notion_api_key")
    parent_page_id = request.json.get("parent_page_id", "").strip() if request.is_json else request.form.get("parent_page_id", "").strip()
    if not api_key:
        return jsonify({"error": "Save your Notion API key first."}), 400
    if not parent_page_id:
        return jsonify({"error": "Parent page ID is required."}), 400
    try:
        ids = setup_notion_workspace(api_key, parent_page_id)
        update_user_keys(request.user["id"], ids)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/run", methods=["POST"])
@login_required
def run_analysis():
    user = dict(request.user)
    threading.Thread(target=_run_for_user, args=(user,), daemon=True).start()
    return "", 204

def _run_for_user(user):
    import core.logger as logger
    env_map = {
        "ANTHROPIC_API_KEY": "anthropic_api_key",
        "NOTION_API_KEY": "notion_api_key",
        "ALPHA_VANTAGE_API_KEY": "alpha_vantage_api_key",
        "WATCHLIST_DB_ID": "watchlist_db_id",
        "RESEARCH_NOTES_DB_ID": "research_notes_db_id",
        "EARNINGS_CALENDAR_DB_ID": "earnings_calendar_db_id",
        "DAILY_DIGEST_DB_ID": "daily_digest_db_id",
    }
    for env_key, user_key in env_map.items():
        val = user.get(user_key)
        if val:
            os.environ[env_key] = val

    import importlib, config, main, tools.notion, tools.prices, tools.news, core.agent
    for mod in [config, tools.notion, tools.prices, tools.news, core.agent, main]:
        importlib.reload(mod)

    try:
        main.run()
    except Exception as e:
        logger.error(str(e))
    finally:
        logger.log_queue.put("__done__")

@app.route("/api/logs")
@login_required
def log_stream():
    import queue
    import core.logger as logger

    def stream():
        while True:
            try:
                msg = logger.log_queue.get(timeout=10)
                yield f"data: {msg}\n\n"
                if msg == "__done__":
                    break
            except queue.Empty:
                yield ": keepalive\n\n"

    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    init_db()
    from scheduler import start
    start()
    app.run(debug=True)
