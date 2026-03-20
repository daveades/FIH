import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

WATCHLIST_DB_ID = os.getenv("WATCHLIST_DB_ID")
RESEARCH_NOTES_DB_ID = os.getenv("RESEARCH_NOTES_DB_ID")
EARNINGS_CALENDAR_DB_ID = os.getenv("EARNINGS_CALENDAR_DB_ID")
DAILY_DIGEST_DB_ID = os.getenv("DAILY_DIGEST_DB_ID")

MODEL = "claude-sonnet-4-20250514"
