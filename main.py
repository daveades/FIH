from datetime import date
from tools.notion import get_watchlist, update_watchlist_row, create_research_note, create_earnings_entry, create_daily_digest
from tools.prices import get_earnings_date
from agent import analyse_ticker, generate_earnings_brief, generate_daily_digest
import logger

def run():
    today = str(date.today())
    watchlist = get_watchlist()
    logger.section("starting run")
    logger.info(f"found {len(watchlist)} tickers")

    analyses = []

    for stock in watchlist:
        ticker = stock["ticker"]
        logger.info(f"analysing {ticker}...")

        result = analyse_ticker(ticker)
        analyses.append(result)

        update_watchlist_row(
            stock["id"],
            result["price"],
            result["change_percent"],
            result["sentiment"],
            result["score"],
            result["summary"]
        )

        create_research_note(
            stock["id"],
            ticker,
            today,
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
