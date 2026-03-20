from datetime import date
from tools.notion import get_watchlist, update_watchlist_row, create_research_note
from agent import analyse_ticker

def run():
    watchlist = get_watchlist()
    print(f"found {len(watchlist)} tickers")

    for stock in watchlist:
        ticker = stock["ticker"]
        print(f"analysing {ticker}...")

        result = analyse_ticker(ticker)

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
            str(date.today()),
            result["bull_case"],
            result["bear_case"],
            result["risk_level"],
            result["summary"]
        )

        print(f"done with {ticker}")

if __name__ == "__main__":
    run()
