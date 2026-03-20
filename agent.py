import anthropic
from config import ANTHROPIC_API_KEY, MODEL
from tools.prices import get_price
from tools.news import get_news
from prompts import ticker_analysis_prompt

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def parse_analysis(text):
    result = {}
    for line in text.splitlines():
        if line.startswith("SENTIMENT:"):
            result["sentiment"] = line.split(":", 1)[1].strip()
        elif line.startswith("SCORE:"):
            result["score"] = line.split(":", 1)[1].strip()
        elif line.startswith("SUMMARY:"):
            result["summary"] = line.split(":", 1)[1].strip()
        elif line.startswith("BULL CASE:"):
            result["bull_case"] = line.split(":", 1)[1].strip()
        elif line.startswith("BEAR CASE:"):
            result["bear_case"] = line.split(":", 1)[1].strip()
        elif line.startswith("RISK:"):
            result["risk_level"] = line.split(":", 1)[1].strip()
    return result

def analyse_ticker(ticker):
    price_data = get_price(ticker)
    news = get_news(ticker)

    prompt = ticker_analysis_prompt(
        ticker,
        price_data["price"],
        price_data["change_percent"],
        news
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return parse_analysis(response.content[0].text)
