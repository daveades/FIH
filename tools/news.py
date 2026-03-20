import anthropic
from config import ANTHROPIC_API_KEY, MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_news(ticker):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"Find the latest news about {ticker} stock from the past 24 hours. Summarise the key points briefly."
        }]
    )

    for block in response.content:
        if block.type == "text":
            return block.text

    return ""
