import time
import anthropic
from config import ANTHROPIC_API_KEY, MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_news(ticker):
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"Search for latest stock news about {ticker} today. Reply with exactly:\nHEADLINES: top 2 headlines\nSUMMARY: one sentence summary\nSOURCE: one url\nSENTIMENT: Bullish, Bearish, or Neutral"
        }]
    )
    raw = " ".join(
        block.text for block in response.content
        if getattr(block, "type", "") == "text" and hasattr(block, "text")
    ).strip()
    return parse_news(ticker, raw)

def parse_news(ticker, raw):
    import re
    result = {"ticker": ticker, "summary": "", "source_url": ""}
    patterns = {
        "summary": r"SUMMARY:\s*(.*?)(?=SOURCE:|SENTIMENT:|$)",
        "source_url": r"SOURCE:\s*(https?://\S+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        if match:
            result[key] = match.group(1).strip()
    return result

def get_news_for_watchlist(watchlist):
    total = len(watchlist)
    print(f"fetching news for {total} tickers (~{total + (total - 1)} mins total)")
    results = {}
    for i, stock in enumerate(watchlist):
        ticker = stock["ticker"]
        print(f"news {i + 1}/{total}: {ticker}")
        results[ticker] = get_news(ticker)
        if i < total - 1:
            print(f"waiting 65 seconds...")
            time.sleep(65)
    return results
