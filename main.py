import time
from datetime import date
from tools.notion import get_watchlist, update_watchlist_row, create_research_note, create_earnings_entry, create_daily_digest
from tools.prices import get_prices_for_watchlist, get_earnings_date
from tools.news import get_news_for_watchlist
from agent import analyse_ticker, generate_earnings_brief, generate_daily_digest
import logger

def run():
    today = str(date.today())
    watchlist = get_watchlist()
    logger.section("starting run")
    logger.info(f"found {len(watchlist)} tickers")

    logger.section("fetching prices")
    prices = get_prices_for_watchlist(watchlist)

    logger.section("fetching news")
    news = get_news_for_watchlist(watchlist)

    logger.section("waiting before analysis")
    time.sleep(65)

    logger.section("running analysis")
    analyses = []

    for i, stock in enumerate(watchlist):
        ticker = stock["ticker"]
        logger.info(f"analysing {ticker}...")

        news_data = news.get(ticker, {})
        result = analyse_ticker(ticker, prices.get(ticker, {}), news_data.get("summary", ""))
        analyses.append(result)

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

        earnings = get_earnings_date(ticker)
        if earnings:
            generate_earnings_brief(
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
                earnings["expected_eps"]
            )
            logger.success(f"earnings brief done for {ticker}")

        logger.success(f"done with {ticker}")

        if i < len(watchlist) - 1:
            time.sleep(15)

    logger.section("generating daily digest")
    digest = generate_daily_digest(analyses)
    create_daily_digest(
        today,
        digest["mood"],
        digest["top_movers"],
        digest["biggest_risks"],
        digest["full_briefing"],
        digest["action_items"]
    )
    logger.success("all done")

if __name__ == "__main__":
    run()
