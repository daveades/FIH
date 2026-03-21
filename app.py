import threading
from flask import Flask, render_template, Response, jsonify
from tools.notion import get_watchlist
from logger import log_queue
import main as pipeline

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def status():
    watchlist = get_watchlist()
    return jsonify({"tickers": watchlist})

@app.route("/api/run", methods=["POST"])
def run_pipeline():
    def run():
        pipeline.run()
    threading.Thread(target=run, daemon=True).start()
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
