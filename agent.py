import anthropic
from config import ANTHROPIC_API_KEY, MODEL
from prompts import ticker_analysis_prompt, earnings_brief_prompt, daily_digest_prompt

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

REQUIRED_KEYS = {"sentiment", "score", "summary", "bull_case", "bear_case", "risk_level"}

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
    return result if REQUIRED_KEYS.issubset(result) else None

def analyse_ticker(ticker, price_data, news):
    prompt = ticker_analysis_prompt(
        ticker,
        price_data.get("price"),
        price_data.get("change_percent"),
        news
    )

    for _ in range(3):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        result = parse_analysis(response.content[0].text)
        if result:
            result["price"] = price_data.get("price")
            result["change_percent"] = price_data.get("change_percent")
            result["ticker"] = ticker
            return result

    raise ValueError(f"Claude did not return a valid analysis for {ticker} after 3 attempts")

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
    current_key = None
    current_value = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("MARKET MOOD:"):
            current_key = "mood"
            current_value = [line.split(":", 1)[1].strip()]
        elif line.startswith("TOP MOVERS:"):
            if current_key: result[current_key] = " ".join(current_value)
            current_key = "top_movers"
            current_value = [line.split(":", 1)[1].strip()]
        elif line.startswith("BIGGEST RISKS:"):
            if current_key: result[current_key] = " ".join(current_value)
            current_key = "biggest_risks"
            current_value = [line.split(":", 1)[1].strip()]
        elif line.startswith("ACTION ITEMS:"):
            if current_key: result[current_key] = " ".join(current_value)
            current_key = "action_items"
            current_value = [line.split(":", 1)[1].strip()]
        elif line.startswith("FULL BRIEFING:"):
            if current_key: result[current_key] = " ".join(current_value)
            current_key = "full_briefing"
            current_value = [line.split(":", 1)[1].strip()]
        else:
            if current_key:
                current_value.append(line)

    if current_key:
        result[current_key] = " ".join(current_value)

    return result
