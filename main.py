import time
from datetime import date
from tools.notion import get_watchlist, update_watchlist_row, create_research_note, create_earnings_entry, create_daily_digest, earnings_entry_exists, get_unreported_past_earnings, mark_as_reported, get_earnings_this_week
from tools.prices import get_market_data_for_watchlist
from tools.news import get_news_for_watchlist
from core.agent import analyse_ticker, generate_earnings_brief, generate_earnings_summary, generate_daily_digest
import core.logger as logger

def run():
    today = str(date.today())

    logger.section("starting run")
    logger.info(f"date: {today}")

    watchlist = get_watchlist()
    logger.info(f"{len(watchlist)} tickers on watchlist: {', '.join(s['ticker'] for s in watchlist)}")

    logger.section("fetching market data")
    prices, earnings_data = get_market_data_for_watchlist(watchlist)
    for stock in watchlist:
        t = stock["ticker"]
        p = prices.get(t, {})
        price = p.get("price")
        change = p.get("change_percent")
        if price:
            logger.info(f"{t}: ${price}  {change}")
        else:
            logger.info(f"{t}: price unavailable")

    logger.section("fetching news")
    news = get_news_for_watchlist(watchlist)
    for stock in watchlist:
        t = stock["ticker"]
        n = news.get(t, {})
        summary = n.get("summary", "")
        if summary:
            logger.info(f"{t}: {summary[:120]}{'...' if len(summary) > 120 else ''}")
        else:
            logger.info(f"{t}: no news found")

    logger.section("waiting 65s before analysis (rate limit)")
    time.sleep(65)

    logger.section("processing reported earnings")
    past_earnings = get_unreported_past_earnings()
    if not past_earnings:
        logger.info("no unreported past earnings found")
    for entry in past_earnings:
        ticker = entry["company"].split("(")[-1].rstrip(")") if "(" in entry["company"] else entry["company"]
        logger.info(f"writing earnings summary for {entry['company']} (reported {entry['report_date']})")
        news_data = news.get(ticker, {})
        summary = generate_earnings_summary(ticker, entry["company"], entry["report_date"], news_data.get("summary", ""))
        mark_as_reported(entry["id"], summary)
        logger.success(f"earnings summary saved for {entry['company']}")

    logger.section("running analysis")
    analyses = []
    flagged_ids = []

    for i, stock in enumerate(watchlist):
        ticker = stock["ticker"]
        logger.info(f"[{i+1}/{len(watchlist)}] analysing {ticker}...")

        news_data = news.get(ticker, {})
        result = analyse_ticker(ticker, prices.get(ticker, {}), news_data.get("summary", ""))
        analyses.append(result)

        logger.info(f"{ticker} → sentiment: {result['sentiment']}  score: {result['score']}/10  risk: {result['risk_level']}")
        logger.info(f"{ticker} → bull: {result['bull_case'][:90]}")
        logger.info(f"{ticker} → bear: {result['bear_case'][:90]}")

        if result.get("alert"):
            logger.info(f"{ticker} → ALERT flagged")
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
        logger.info(f"{ticker} → watchlist updated")

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
        logger.info(f"{ticker} → research note saved")

        earnings = earnings_data.get(ticker)
        if earnings and earnings["report_date"] > today and not earnings_entry_exists(stock["id"]):
            logger.info(f"{ticker} → earnings report due {earnings['report_date']}, generating brief...")
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
            logger.success(f"{ticker} → earnings entry created  watch closely: {brief['watch_closely']}")
        elif earnings and earnings["report_date"] <= today:
            logger.info(f"{ticker} → earnings already reported, skipping")
        elif earnings:
            logger.info(f"{ticker} → earnings entry already exists, skipping")
        else:
            logger.info(f"{ticker} → no upcoming earnings found")

        logger.success(f"{ticker} done")

        if i < len(watchlist) - 1:
            logger.info(f"waiting 15s before next ticker...")
            time.sleep(15)

    logger.section("generating daily digest")
    digest = generate_daily_digest(analyses)
    logger.info(f"market mood: {digest.get('mood', '—')}")
    logger.info(f"top movers: {digest.get('top_movers', '')[:120]}")
    logger.info(f"flagged tickers: {len(flagged_ids)}")

    earnings_ids = get_earnings_this_week()
    logger.info(f"earnings this week: {len(earnings_ids)}")

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
    logger.success("daily digest saved to Notion")
    logger.success("run complete")

if __name__ == "__main__":
    run()
