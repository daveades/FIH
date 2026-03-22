from datetime import date, datetime, timedelta
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

def update_watchlist_row(page_id, price, change_percent, sentiment, score, summary, alert=False):
    properties = {
        "Sentiment Label": {"select": {"name": sentiment}},
        "Sentiment Score": {"number": float(score)},
        "Last AI Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]},
        "Last Updated": {"date": {"start": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}},
        "Alert Flag": {"checkbox": alert}
    }
    if price:
        properties["Current Price"] = {"number": float(price)}
        properties["Price Change %"] = {"number": float(change_percent.replace("%", "")) if change_percent else None}
    notion.pages.update(page_id=page_id, properties=properties)

def create_research_note(ticker_page_id, ticker, timestamp, date, news_url, key_signals, bull_case, bear_case, risk_level, full_analysis):
    notion.pages.create(
        parent={"database_id": RESEARCH_NOTES_DB_ID},
        properties={
            "Title": {"title": [{"text": {"content": f"{ticker} — {timestamp}"}}]},
            "Ticker": {"relation": [{"id": ticker_page_id}]},
            "Date": {"date": {"start": timestamp}},
            "News Sources": {"url": news_url if news_url and news_url.startswith("http") else None},
            "Key Signals": {"rich_text": [{"text": {"content": key_signals[:2000]}}]},
            "Bull Case": {"rich_text": [{"text": {"content": bull_case[:2000]}}]},
            "Bear Case": {"rich_text": [{"text": {"content": bear_case[:2000]}}]},
            "Risk Level": {"select": {"name": risk_level}},
            "Full Analysis": {"rich_text": [{"text": {"content": full_analysis[:2000]}}]}
        }
    )

def get_unreported_past_earnings():
    today = date.today().isoformat()
    response = notion.databases.query(
        database_id=EARNINGS_CALENDAR_DB_ID,
        filter={
            "and": [
                {"property": "Report Date", "date": {"before": today}},
                {"property": "Status", "select": {"equals": "Upcoming"}}
            ]
        }
    )
    results = []
    for page in response["results"]:
        props = page["properties"]
        company = props["Company"]["title"][0]["text"]["content"] if props["Company"]["title"] else ""
        report_date = props["Report Date"]["date"]["start"] if props["Report Date"]["date"] else ""
        results.append({"id": page["id"], "company": company, "report_date": report_date})
    return results

def mark_as_reported(page_id, summary):
    notion.pages.update(
        page_id=page_id,
        properties={
            "Status": {"select": {"name": "Reported"}},
            "Earnings Summary": {"rich_text": [{"text": {"content": summary[:2000]}}]}
        }
    )

def earnings_entry_exists(ticker_page_id):
    today = date.today().isoformat()
    response = notion.databases.query(
        database_id=EARNINGS_CALENDAR_DB_ID,
        filter={
            "and": [
                {"property": "Ticker", "relation": {"contains": ticker_page_id}},
                {"property": "Report Date", "date": {"on_or_after": today}},
                {"property": "Status", "select": {"equals": "Upcoming"}}
            ]
        }
    )
    return len(response["results"]) > 0

def create_earnings_entry(ticker_page_id, company, ticker, report_date, expected_eps, brief="", watch_closely=False):
    properties = {
        "Company": {"title": [{"text": {"content": company}}]},
        "Ticker": {"relation": [{"id": ticker_page_id}]},
        "Report Date": {"date": {"start": report_date}},
        "Status": {"select": {"name": "Upcoming"}},
        "Watch Closely": {"checkbox": watch_closely}
    }
    if expected_eps is not None:
        properties["Expected EPS"] = {"number": expected_eps}
    if brief:
        properties["Pre Earnings Brief"] = {"rich_text": [{"text": {"content": brief[:2000]}}]}
    notion.pages.create(parent={"database_id": EARNINGS_CALENDAR_DB_ID}, properties=properties)

def get_earnings_this_week():
    today = date.today().isoformat()
    week_end = (date.today() + timedelta(days=7)).isoformat()
    response = notion.databases.query(
        database_id=EARNINGS_CALENDAR_DB_ID,
        filter={
            "and": [
                {"property": "Report Date", "date": {"on_or_after": today}},
                {"property": "Report Date", "date": {"before": week_end}},
                {"property": "Status", "select": {"equals": "Upcoming"}}
            ]
        }
    )
    return [page["id"] for page in response["results"]]

def create_daily_digest(date, mood, top_movers, biggest_risks, full_briefing, action_items, flagged_ids=None, earnings_ids=None):
    properties = {
        "Date": {"title": [{"text": {"content": date}}]},
        "Market Mood": {"select": {"name": mood}},
        "Top Movers": {"rich_text": [{"text": {"content": top_movers[:2000]}}]},
        "Biggest Risks Today": {"rich_text": [{"text": {"content": biggest_risks[:2000]}}]},
        "Full Briefing": {"rich_text": [{"text": {"content": full_briefing[:2000]}}]},
        "Action Items": {"rich_text": [{"text": {"content": action_items[:2000]}}]},
        "Last Updated": {"date": {"start": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}},
        "Tickers Flagged": {"relation": [{"id": tid} for tid in (flagged_ids or [])]},
        "Earnings This Week": {"relation": [{"id": eid} for eid in (earnings_ids or [])]}
    }
    existing = notion.databases.query(
        database_id=DAILY_DIGEST_DB_ID,
        filter={"property": "Date", "title": {"equals": date}}
    )
    if existing["results"]:
        notion.pages.update(page_id=existing["results"][0]["id"], properties=properties)
    else:
        notion.pages.create(parent={"database_id": DAILY_DIGEST_DB_ID}, properties=properties)
