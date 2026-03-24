from apscheduler.schedulers.background import BackgroundScheduler
from web.db import get_all_users
import core.logger as logger

def run_all_users():
    from app import _run_for_user
    users = get_all_users()
    logger.section(f"scheduled run — {len(users)} user(s)")
    for user in users:
        if all(user.get(k) for k in ["anthropic_api_key", "notion_api_key", "alpha_vantage_api_key",
                                      "watchlist_db_id", "research_notes_db_id",
                                      "earnings_calendar_db_id", "daily_digest_db_id"]):
            logger.info(f"running for {user['email']}")
            _run_for_user(dict(user))
        else:
            logger.info(f"skipping {user['email']} — keys not fully configured")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_all_users, "cron", hour=9,  minute=0)
    scheduler.add_job(run_all_users, "cron", hour=20, minute=0)
    scheduler.start()
    return scheduler
