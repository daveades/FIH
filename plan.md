# Finance Intelligence Hub - Plan

## What I'm trying to do

I spend too much time manually checking stocks, reading news, and trying to figure out if something is worth paying attention to. I want something that does that for me every day and puts the findings somewhere I can actually read them without opening 10 tabs.

The idea is simple: I have a list of stocks I care about. Every day, I want a summary of what's going on with each one — price movement, latest news, any risks. And I want it all in Notion because that's where I already organize everything.

## The core pieces

1. **A watchlist** — somewhere to store tickers of interest.
2. **Price data** — pull current price and % change for each ticker
3. **News** — find out what's been said about each stock recently
4. **AI analysis** — feed the price + news to Claude and get a plain-english take: sentiment, risks, bull/bear case
5. **Store it** — write the analysis back to Notion
6. **Earnings** — flag when a company is about to report earnings, generate a pre-earnings brief
7. **Daily digest** — one summary at the end that gives me the big picture for the day
8. **Web dashboard** — a simple UI so I can trigger a run and watch it happen live

## How I'll build it

Start with the basics — get one ticker's price, then get news for it, then get Claude to say something useful about it. Once that works end-to-end for one ticker, expand to a list. Add Notion storage once the analysis is working. Build the web UI last.

## APIs I'll need

- Anthropic (Claude) — for analysis and web search
- Alpha Vantage — for price data and earnings dates
- Notion — for storage and display

## What I'll figure out as I go

- Exactly how to structure the Notion databases
- How to handle rate limits gracefully
- Whether the AI prompt needs tuning after seeing real output
- Scheduling (maybe cron, maybe manual for now)
