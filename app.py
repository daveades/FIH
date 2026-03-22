import schedule
import threading
import time
from flask import Flask, render_template, Response, jsonify
from tools.notion import get_watchlist
from logger import log_queue
import logger
import main as pipeline

app = Flask(__name__)
is_running = False

def run_pipeline_job():
    global is_running
    if is_running:
        return
    is_running = True
    try:
        pipeline.run()
    finally:
        is_running = False
        logger.info("__done__")

def start_scheduler():
    schedule.every().day.at("09:00").do(lambda: threading.Thread(target=run_pipeline_job, daemon=True).start())
    schedule.every().day.at("21:00").do(lambda: threading.Thread(target=run_pipeline_job, daemon=True).start())
    while True:
        schedule.run_pending()
        time.sleep(30)

threading.Thread(target=start_scheduler, daemon=True).start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def status():
    watchlist = get_watchlist()
    return jsonify({"tickers": watchlist})

@app.route("/api/run", methods=["POST"])
def run_now():
    if is_running:
        return jsonify({"status": "already running"})
    threading.Thread(target=run_pipeline_job, daemon=True).start()
    return jsonify({"status": "started"})

@app.route("/api/logs")
def logs():
    def stream():
        while True:
            msg = log_queue.get()
            yield f"data: {msg}\n\n"
    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
