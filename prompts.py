def ticker_analysis_prompt(ticker, price, change_percent, news):
    return f"""You are a financial analyst. Analyse the following stock and return your findings in this exact format:

SENTIMENT: <Bullish/Bearish/Neutral>
SCORE: <number from 1 to 10>
SUMMARY: <2-3 sentence plain english summary>
BULL CASE: <one sentence>
BEAR CASE: <one sentence>
RISK LEVEL: <Low/Medium/High>
ALERT: <true if this stock needs immediate attention, false otherwise>

Stock: {ticker}
Current Price: {price}
Change: {change_percent}
Recent News:
{news}"""


def earnings_brief_prompt(ticker, company, report_date, analysis):
    return f"""You are a financial analyst preparing a pre-earnings brief.

Company: {company} ({ticker})
Report Date: {report_date}
Recent Analysis:
{analysis}

Write a short pre-earnings brief using this format:

WHAT TO WATCH: <one sentence on the key thing to look for>
EXPECTATIONS: <one sentence on what the market expects>
RISK IF MISS: <one sentence on downside if they disappoint>
RISK IF BEAT: <one sentence on upside if they surprise>"""


def daily_digest_prompt(analyses):
    combined = "\n\n".join(
        f"{a['ticker']}: {a['summary']} | Sentiment: {a['sentiment']} | Risk: {a['risk_level']}"
        for a in analyses
    )
    return f"""You are a financial analyst writing a daily market briefing.

Here are today's stock analyses:
{combined}

Write a daily digest using this exact format:

MARKET MOOD: <Bullish/Bearish/Mixed>
TOP MOVERS: <2-3 sentences on the most notable stocks today>
BIGGEST RISKS: <1-2 sentences on key risks to watch>
ACTION ITEMS: <2-3 bullet points of things to act on or monitor>
FULL BRIEFING: <a short paragraph summarising the overall market picture>"""
