from notion_client import Client

def setup_notion_workspace(api_key, parent_page_id):
    notion = Client(auth=api_key)
    parent_id = parent_page_id.replace("-", "")

    # Watchlist — identifier and signals first, then price data, then summary
    watchlist = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Watchlist"}}],
        properties={
            "Ticker":          {"title": {}},
            "Company Name":    {"rich_text": {}},
            "Sector":          {"select": {}},
            "Current Price":   {"number": {"format": "dollar"}},
            "Price Change %":  {"number": {"format": "percent"}},
            "Sentiment Score": {"number": {}},
            "Sentiment Label": {"select": {"options": [
                {"name": "Bullish", "color": "green"},
                {"name": "Bearish", "color": "red"},
                {"name": "Neutral", "color": "gray"}
            ]}},
            "Last AI Summary": {"rich_text": {}},
            "Alert Flag":      {"checkbox": {}},
            "Last Updated":    {"date": {}}
        }
    )
    watchlist_id = watchlist["id"]

    # Research Notes — identity and date first, signals, cases, then full text
    research_notes = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Research Notes"}}],
        properties={
            "Title":         {"title": {}},
            "Ticker":        {"relation": {"database_id": watchlist_id, "type": "single_property", "single_property": {}}},
            "Date":          {"date": {}},
            "News Sources":  {"url": {}},
            "Bear Case":     {"rich_text": {}},
            "Bull Case":     {"rich_text": {}},
            "Full Analysis": {"rich_text": {}},
            "Key Signals":   {"rich_text": {}},
            "Risk Level":    {"select": {"options": [
                {"name": "Low",    "color": "green"},
                {"name": "Medium", "color": "yellow"},
                {"name": "High",   "color": "red"}
            ]}}
        }
    )
    research_notes_id = research_notes["id"]

    # Earnings Calendar — event details first, then watch flag, then brief and summary
    earnings_calendar = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Earnings Calendar"}}],
        properties={
            "Company":            {"title": {}},
            "Ticker":             {"relation": {"database_id": watchlist_id, "type": "single_property", "single_property": {}}},
            "Expected EPS":       {"number": {}},
            "Report Date":        {"date": {}},
            "Pre Earnings Brief": {"rich_text": {}},
            "Earnings Summary":   {"rich_text": {}},
            "Watch Closely":      {"checkbox": {}},
            "Status":             {"select": {"options": [
                {"name": "Upcoming", "color": "blue"},
                {"name": "Reported", "color": "green"}
            ]}}
        }
    )
    earnings_id = earnings_calendar["id"]

    # Daily Digest — date and mood first, relations, then briefing content
    daily_digest = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Daily Digest"}}],
        properties={
            "Date":                {"title": {}},
            "Last Updated":        {"date": {}},
            "Biggest Risks Today": {"rich_text": {}},
            "Market Mood":         {"select": {"options": [
                {"name": "Bullish", "color": "green"},
                {"name": "Bearish", "color": "red"},
                {"name": "Mixed",   "color": "yellow"}
            ]}},
            "Top Movers":          {"rich_text": {}},
            "Full Briefing":       {"rich_text": {}},
            "Action Items":        {"rich_text": {}},
            "Tickers Flagged":     {"relation": {"database_id": watchlist_id, "type": "single_property", "single_property": {}}},
            "Earnings This Week":  {"relation": {"database_id": earnings_id,  "type": "single_property", "single_property": {}}}
        }
    )
    daily_digest_id = daily_digest["id"]

    return {
        "watchlist_db_id":         watchlist_id,
        "research_notes_db_id":    research_notes_id,
        "earnings_calendar_db_id": earnings_id,
        "daily_digest_db_id":      daily_digest_id
    }
