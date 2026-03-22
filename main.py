import time
from datetime import date
from tools.notion import get_watchlist, update_watchlist_row, create_research_note, create_earnings_entry, create_daily_digest, earnings_entry_exists, get_unreported_past_earnings, mark_as_reported, get_earnings_this_week
from tools.prices import get_market_data_for_watchlist
from tools.news import get_news_for_watchlist
from core.agent import analyse_ticker, generate_earnings_brief, generate_earnings_summary, generate_daily_digest
import core.logger as logger

def run():
    today = str(date.today())
    watchlist = get_watchlist()
    logger.section("starting run")
    logger.info(f"found {len(watchlist)} tickers")

    logger.section("fetching market data")
    prices, earnings_data = get_market_data_for_watchlist(watchlist)

    logger.section("fetching news")
    news = get_news_for_watchlist(watchlist)

    logger.section("waiting before analysis")
    time.sleep(65)

    logger.section("processing reported earnings")
    past_earnings = get_unreported_past_earnings()
    for entry in past_earnings:
        ticker = entry["company"].split("(")[-1].rstrip(")") if "(" in entry["company"] else entry["company"]
        news_data = news.get(ticker, {})
        summary = generate_earnings_summary(ticker, entry["company"], entry["report_date"], news_data.get("summary", ""))
        mark_as_reported(entry["id"], summary)
        logger.success(f"earnings summary written for {entry['company']}")

    logger.section("running analysis")
    analyses = []
    flagged_ids = []

    for i, stock in enumerate(watchlist):
        ticker = stock["ticker"]
        logger.info(f"analysing {ticker}...")

        news_data = news.get(ticker, {})
        result = analyse_ticker(ticker, prices.get(ticker, {}), news_data.get("summary", ""))
        analyses.append(result)
        if result.get("alert"):
            flagged_ids.append(stock["id"])

        update_watchlist_row(
            stock["id"],
            result["price"],
            result["change_percent"],
            result["sentiment"],
            result["score"],
            result["summary"],
            result.get("alert", False)
        )

        create_research_note(
            stock["id"],
            ticker,
            today,
            news_data.get("source_url", ""),
            result["summary"],
            result["bull_case"],
            result["bear_case"],
            result["risk_level"],
            result["summary"]
        )

        earnings = earnings_data.get(ticker)
        if earnings and earnings["report_date"] > today and not earnings_entry_exists(stock["id"]):
            brief = generate_earnings_brief(
                ticker,
                stock["company"],
                earnings["report_date"],
                result["summary"]
            )
            create_earnings_entry(
                stock["id"],
                stock["company"],
                ticker,
                earnings["report_date"],
                earnings["expected_eps"],
                brief["brief"],
                brief["watch_closely"]
            )
            logger.success(f"earnings entry created for {ticker}")
        elif earnings:
            logger.info(f"earnings entry already exists for {ticker}, skipping")

        logger.success(f"done with {ticker}")

        if i < len(watchlist) - 1:
            time.sleep(15)

    logger.section("generating daily digest")
    digest = generate_daily_digest(analyses)
    earnings_ids = get_earnings_this_week()
    create_daily_digest(
        today,
        digest["mood"],
        digest["top_movers"],
        digest["biggest_risks"],
        digest["full_briefing"],
        digest["action_items"],
        flagged_ids,
        earnings_ids
    )
    logger.success("all done")

if __name__ == "__main__":
    run()
