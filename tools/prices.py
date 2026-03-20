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
        "price": data.get("price"),
        "change_percent": data.get("change_percent")
    }
