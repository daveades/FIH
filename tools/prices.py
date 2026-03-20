import httpx
from config import ALPHA_VANTAGE_API_KEY

BASE_URL = "https://www.alphavantage.co/query"

def get_price(ticker):
    response = httpx.get(BASE_URL, params={
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": ALPHA_VANTAGE_API_KEY
    })
    data = response.json().get("Global Quote", {})
    return {
        "ticker": ticker,
        "price": data.get("05. price"),
        "change_percent": data.get("10. change percent")
    }

def get_earnings_date(ticker):
    response = httpx.get(BASE_URL, params={
        "function": "EARNINGS_CALENDAR",
        "symbol": ticker,
        "horizon": "3month",
        "apikey": ALPHA_VANTAGE_API_KEY
    })
    lines = response.text.strip().splitlines()
    if len(lines) < 2:
        return None
    for line in lines[1:]:
        parts = line.split(",")
        if parts[0] == ticker:
            return {"report_date": parts[2], "expected_eps": parts[3]}
    return None
