# Agents Documentation

This project uses 6 specialized AI agents running in parallel via CrewAI.

## Agent Overview

| Agent | Role | Tools Used | Output Model |
|-------|------|------------|--------------|
| **Price** | Stock Price Analyst | get_stock_price, get_stock_price_history | `PriceData` |
| **Financial** | Financial Analyst | get_stock_financial_metrics | `FinancialMetrics` |
| **News** | News Analyst | search_financial_news | `NewsAnalysis` |
| **Market** | Market Trend Analyst | get_price_history, search_news | `MarketTrends` |
| **Sentiment** | Sentiment Analyst | analyze_sentiment, get_social_mentions, search_news | `SentimentData` |
| **Risk** | Risk Analyst | analyze_risk, get_price_history | `RiskAssessment` |
| **Synthesis** | Report Editor | (none) | `ResearchReport` |

## Price Agent

**Role:** Stock Price Analyst

**Goal:** Get real-time stock price and trading data

**Tools:**
- `get_stock_price`: Current price, volume, market cap
- `get_stock_price_history`: Historical price data

**Output Model:** `PriceData`
```python
{
    "ticker": "AAPL",
    "current_price": 175.43,
    "volume": 52340000,
    "market_cap": 2750000000000,
    "week_52_high": 199.62,
    "week_52_low": 124.17,
    ...
}
```

## Financial Agent

**Role:** Financial Analyst

**Goal:** Analyze financial metrics and company fundamentals

**Tools:**
- `get_stock_financial_metrics`: P/E, EPS, revenue, dividends

**Output Model:** `FinancialMetrics`
```python
{
    "ticker": "AAPL",
    "pe_ratio": 28.5,
    "profit_margin": 0.25,
    "revenue": 383000000000,
    "dividend_yield": 0.52,
    ...
}
```

## News Agent

**Role:** News Analyst

**Goal:** Find and analyze latest news and developments

**Tools:**
- `search_financial_news`: Search news via Tavily API

**Output Model:** `NewsAnalysis`
```python
{
    "ticker": "AAPL",
    "articles": [...],
    "sentiment": "positive",
    "key_developments": [...],
    ...
}
```

## Market Agent

**Role:** Market Trend Analyst

**Goal:** Analyze market position, trends, and technical indicators

**Tools:**
- `get_price_history`: Historical prices for technical analysis
- `search_news`: Market sentiment from news

**Output Model:** `MarketTrends`

## Sentiment Agent

**Role:** Sentiment Analyst

**Goal:** Analyze market sentiment from social media and news sources

**Tools:**
- `analyze_sentiment`: Overall sentiment analysis
- `get_social_mentions`: Reddit, Twitter mentions
- `search_news`: News sentiment

**Output Model:** `SentimentData`

## Risk Agent

**Role:** Risk Analyst

**Goal:** Quantify and assess investment risks using statistical metrics

**Tools:**
- `analyze_risk`: Calculate risk metrics
- `get_price_history`: Historical data for volatility calculation

**Output Model:** `RiskAssessment`

## Synthesis Agent

**Role:** Investment Report Editor

**Goal:** Compile research findings into a comprehensive report

**Tools:** None (uses LLM to synthesize)

**Output Model:** `ResearchReport`
```python
{
    "ticker": "AAPL",
    "executive_summary": "...",
    "recommendation": "Buy",
    "rating": "Buy",
    "risk_level": "Moderate",
    "price_target": 190.00,
    ...
}
```
