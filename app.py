from flask import Flask

app = Flask(__name__)

# TODO: index route — serve a simple dashboard page
# TODO: /api/run — trigger a pipeline run in the background
# TODO: /api/status — return current watchlist data for the UI
# TODO: /api/logs — stream logs to the browser using SSE so we can watch it run live

if __name__ == "__main__":
    app.run(debug=True)
