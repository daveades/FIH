def ticker_analysis_prompt(ticker, price, change_percent, news):
    return f"""You are a financial analyst. Analyse the following stock and return your findings in this exact format:

SENTIMENT: <Bullish/Bearish/Neutral>
SCORE: <number from 1 to 10>
SUMMARY: <2-3 sentence plain english summary>
BULL CASE: <one sentence>
BEAR CASE: <one sentence>
RISK LEVEL: <Low/Medium/High>

Stock: {ticker}
Current Price: {price}
Change: {change_percent}
Recent News:
{news}"""


def daily_digest_prompt(analyses):
    # TODO: daily digest prompt
    pass


def earnings_brief_prompt(ticker, company, report_date, analysis):
    # TODO: earnings brief prompt
    pass
