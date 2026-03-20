from notion_client import Client
from config import NOTION_API_KEY, WATCHLIST_DB_ID, RESEARCH_NOTES_DB_ID, EARNINGS_CALENDAR_DB_ID, DAILY_DIGEST_DB_ID

notion = Client(auth=NOTION_API_KEY)

def get_watchlist():
    response = notion.databases.query(database_id=WATCHLIST_DB_ID)
    tickers = []
    for page in response["results"]:
        props = page["properties"]
        tickers.append({
            "id": page["id"],
            "ticker": props["Ticker"]["title"][0]["text"]["content"],
            "company": props["Company Name"]["rich_text"][0]["text"]["content"]
        })
    return tickers

def update_watchlist_row(page_id, price, change_percent, sentiment, score, summary):
    notion.pages.update(
        page_id=page_id,
        properties={
            "Current Price": {"number": float(price)},
            "Price Change %": {"number": float(change_percent.replace("%", ""))},
            "Sentiment Label": {"select": {"name": sentiment}},
            "Sentiment Score": {"number": float(score)},
            "Last AI Summary": {"rich_text": [{"text": {"content": summary}}]}
        }
    )

def create_research_note(ticker_page_id, ticker, date, bull_case, bear_case, risk_level, full_analysis):
    notion.pages.create(
        parent={"database_id": RESEARCH_NOTES_DB_ID},
        properties={
            "Title": {"title": [{"text": {"content": f"{ticker} — {date}"}}]},
            "Ticker": {"relation": [{"id": ticker_page_id}]},
            "Date": {"date": {"start": date}},
            "Bull Case": {"rich_text": [{"text": {"content": bull_case}}]},
            "Bear Case": {"rich_text": [{"text": {"content": bear_case}}]},
            "Risk Level": {"select": {"name": risk_level}},
            "Full Analysis": {"rich_text": [{"text": {"content": full_analysis}}]}
        }
    )

def create_earnings_entry(ticker_page_id, company, ticker, report_date, expected_eps):
    notion.pages.create(
        parent={"database_id": EARNINGS_CALENDAR_DB_ID},
        properties={
            "Company": {"title": [{"text": {"content": company}}]},
            "Ticker": {"relation": [{"id": ticker_page_id}]},
            "Report Date": {"date": {"start": report_date}},
            "Status": {"select": {"name": "Upcoming"}},
            "Expected EPS": {"number": float(expected_eps) if expected_eps else None}
        }
    )

def create_daily_digest(date, mood, top_movers, biggest_risks, full_briefing, action_items):
    notion.pages.create(
        parent={"database_id": DAILY_DIGEST_DB_ID},
        properties={
            "Date": {"title": [{"text": {"content": date}}]},
            "Market Mood": {"select": {"name": mood}},
            "Top Movers": {"rich_text": [{"text": {"content": top_movers}}]},
            "Biggest Risks": {"rich_text": [{"text": {"content": biggest_risks}}]},
            "Full Briefing": {"rich_text": [{"text": {"content": full_briefing}}]},
            "Action Items": {"rich_text": [{"text": {"content": action_items}}]}
        }
    )
