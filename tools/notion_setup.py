from notion_client import Client

def setup_notion_workspace(api_key):
    notion = Client(auth=api_key)

    page = notion.pages.create(
        parent={"type": "workspace", "workspace": True},
        properties={
            "title": {"title": [{"type": "text", "text": {"content": "FIH"}}]}
        }
    )
    parent_id = page["id"]

    watchlist = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Watchlist"}}],
        properties={
            "Ticker":         {"title": {}},
            "Company Name":   {"rich_text": {}},
            "Sector":         {"select": {}},
            "Current Price":  {"number": {"format": "dollar"}},
            "Price Change %": {"number": {"format": "percent"}},
            "Sentiment Score":{"number": {}},
            "Sentiment Label":{"select": {"options": [
                {"name": "Bullish", "color": "green"},
                {"name": "Bearish", "color": "red"},
                {"name": "Neutral", "color": "gray"}
            ]}},
            "Last AI Summary":{"rich_text": {}},
            "Alert Flag":     {"checkbox": {}},
            "Last Updated":   {"date": {}}
        }
    )
    watchlist_id = watchlist["id"]

    research_notes = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Research Notes"}}],
        properties={
            "Title":        {"title": {}},
            "Ticker":       {"relation": {"database_id": watchlist_id, "type": "single_property", "single_property": {}}},
            "Date":         {"date": {}},
            "News Sources": {"url": {}},
            "Key Signals":  {"rich_text": {}},
            "Bull Case":    {"rich_text": {}},
            "Bear Case":    {"rich_text": {}},
            "Risk Level":   {"select": {"options": [
                {"name": "Low",    "color": "green"},
                {"name": "Medium", "color": "yellow"},
                {"name": "High",   "color": "red"}
            ]}},
            "Full Analysis": {"rich_text": {}}
        }
    )
    research_notes_id = research_notes["id"]

    earnings_calendar = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Earnings Calendar"}}],
        properties={
            "Company":           {"title": {}},
            "Ticker":            {"relation": {"database_id": watchlist_id, "type": "single_property", "single_property": {}}},
            "Report Date":       {"date": {}},
            "Status":            {"select": {"options": [
                {"name": "Upcoming", "color": "blue"},
                {"name": "Reported", "color": "green"}
            ]}},
            "Expected EPS":      {"number": {}},
            "Pre Earnings Brief":{"rich_text": {}},
            "Watch Closely":     {"checkbox": {}},
            "Earnings Summary":  {"rich_text": {}}
        }
    )
    earnings_id = earnings_calendar["id"]

    daily_digest = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Daily Digest"}}],
        properties={
            "Date":               {"title": {}},
            "Market Mood":        {"select": {"options": [
                {"name": "Bullish", "color": "green"},
                {"name": "Bearish", "color": "red"},
                {"name": "Mixed",   "color": "yellow"}
            ]}},
            "Top Movers":         {"rich_text": {}},
            "Biggest Risks Today":{"rich_text": {}},
            "Full Briefing":      {"rich_text": {}},
            "Action Items":       {"rich_text": {}},
            "Last Updated":       {"date": {}},
            "Tickers Flagged":    {"relation": {"database_id": watchlist_id, "type": "single_property", "single_property": {}}},
            "Earnings This Week": {"relation": {"database_id": earnings_id,  "type": "single_property", "single_property": {}}}
        }
    )
    daily_digest_id = daily_digest["id"]

    return {
        "watchlist_db_id":          watchlist_id,
        "research_notes_db_id":     research_notes_id,
        "earnings_calendar_db_id":  earnings_id,
        "daily_digest_db_id":       daily_digest_id
    }
