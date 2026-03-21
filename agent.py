import anthropic
from config import ANTHROPIC_API_KEY, MODEL
from tools.prices import get_price
from tools.news import get_news
from prompts import ticker_analysis_prompt, earnings_brief_prompt, daily_digest_prompt

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
        elif line.startswith("RISK LEVEL:"):
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

    result = parse_analysis(response.content[0].text)
    result["price"] = price_data["price"]
    result["change_percent"] = price_data["change_percent"]
    result["ticker"] = ticker
    return result

def generate_earnings_brief(ticker, company, report_date, analysis):
    prompt = earnings_brief_prompt(ticker, company, report_date, analysis)
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def generate_daily_digest(analyses):
    prompt = daily_digest_prompt(analyses)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text
    result = {}
    for line in text.splitlines():
        if line.startswith("MARKET MOOD:"):
            result["mood"] = line.split(":", 1)[1].strip()
        elif line.startswith("TOP MOVERS:"):
            result["top_movers"] = line.split(":", 1)[1].strip()
        elif line.startswith("BIGGEST RISKS:"):
            result["biggest_risks"] = line.split(":", 1)[1].strip()
        elif line.startswith("ACTION ITEMS:"):
            result["action_items"] = line.split(":", 1)[1].strip()
        elif line.startswith("FULL BRIEFING:"):
            result["full_briefing"] = line.split(":", 1)[1].strip()
    return result
