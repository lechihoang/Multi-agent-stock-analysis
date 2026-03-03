# MCP Tools Documentation

This project exposes 10 MCP (Model Context Protocol) tools that LLM agents can call.

## Tool List

| Tool | Description |
|------|-------------|
| `stock_research` | Run full research (calls all 6 agents) |
| `stock_get_price` | Get current stock price, volume, market cap |
| `stock_get_financial_metrics` | Get P/E, EPS, revenue, dividends |
| `stock_search_news` | Search latest news and developments |
| `stock_analyze_sentiment` | Analyze investor sentiment from news & social |
| `stock_analyze_risk` | Calculate volatility, VaR, risk metrics |
| `stock_get_price_history` | Get historical OHLCV data |
| `stock_parse_query` | Extract company name and ticker from query |
| `stock_extract_company` | Extract company name from natural language |
| `stock_lookup_ticker` | Look up ticker symbol by company name |

---

## stock_research

Run full multi-agent research workflow.

**Input:**
```python
query: str  # Natural language query, e.g., "How is Apple doing?"
```

**Output:**
```python
{
    "success": True,
    "ticker": "AAPL",
    "report": {...},  # Full ResearchReport object
    "text_report": "## Research Report\n\n...",
    "execution_time_seconds": 45.2,
    "agents_executed": ["price", "financial", "news", "market", "sentiment", "risk"],
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## stock_get_price

Fetch current stock price and market data.

**Input:**
```python
ticker: str  # Stock ticker, e.g., "AAPL"
```

**Output:**
```python
{
    "success": True,
    "ticker": "AAPL",
    "current_price": 175.43,
    "currency": "USD",
    "day_high": 176.21,
    "day_low": 174.32,
    "volume": 52340000,
    "market_cap": 2750000000000,
    "week_52_high": 199.62,
    "week_52_low": 124.17,
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## stock_get_financial_metrics

Fetch financial fundamentals.

**Input:**
```python
ticker: str  # Stock ticker
```

**Output:**
```python
{
    "success": True,
    "ticker": "AAPL",
    "pe_ratio": 28.5,
    "forward_pe": 24.2,
    "peg_ratio": 1.8,
    "profit_margin": 0.25,
    "revenue": 383000000000,
    "dividend_yield": 0.52,
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## stock_search_news

Search latest financial news.

**Input:**
```python
query: str           # Search query
max_results: int     # Maximum results (default: 10)
```

**Output:**
```python
{
    "success": True,
    "query": "Apple stock news",
    "answer": "Summary of search results...",
    "results": [
        {
            "title": "Apple Reports Record Q4 Earnings",
            "url": "https://...",
            "content": "...",
            "score": 0.95
        }
    ],
    "result_count": 10,
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## stock_analyze_sentiment

Analyze investor sentiment from news and social media.

**Input:**
```python
ticker: str  # Stock ticker
```

**Output:**
```python
{
    "success": True,
    "ticker": "AAPL",
    "sentiment_analysis": {
        "overall_sentiment": "positive",
        "news_sentiment": "positive",
        "social_sentiment": "bullish",
        "key_discussions": [...]
    },
    "social_mentions": {
        "reddit_mentions": [...],
        "twitter_mentions": [...]
    },
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## stock_analyze_risk

Calculate quantitative risk metrics.

**Input:**
```python
ticker: str  # Stock ticker
```

**Output:**
```python
{
    "success": True,
    "ticker": "AAPL",
    "risk_metrics": {
        "volatility": 0.22,
        "beta": 1.28,
        "var_95": 0.045,
        "risk_level": "moderate",
        ...
    },
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## stock_get_price_history

Get historical price data.

**Input:**
```python
ticker: str      # Stock ticker
period: str       # Period (default: "1y"), e.g., "1d", "1w", "1m", "1y", "5y"
```

**Output:**
```python
{
    "success": True,
    "ticker": "AAPL",
    "history": [
        {"date": "2025-02-26", "open": 175.0, "high": 176.0, "low": 174.0, "close": 175.5, "volume": 50000000},
        ...
    ],
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## stock_parse_query

Parse natural language query to extract ticker and agents.

**Input:**
```python
query: str  # Natural language, e.g., "How is Apple doing?"
```

**Output:**
```python
{
    "success": True,
    "original_query": "How is Apple doing?",
    "ticker": "AAPL",
    "agents_needed": ["price", "financial", "news", "market", "sentiment", "risk"],
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## stock_extract_company

Extract company name from query.

**Input:**
```python
query: str  # Natural language query
```

**Output:**
```python
{
    "success": True,
    "original_query": "How is Apple doing?",
    "company_name": "Apple Inc.",
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## stock_lookup_ticker

Look up ticker symbol by company name.

**Input:**
```python
query: str  # Company name, e.g., "Apple"
```

**Output:**
```python
{
    "success": True,
    "query": "Apple",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "exchange": "NASDAQ",
    "timestamp": "2026-02-26T12:00:00"
}
```

---

## Usage Example

### Python

```python
from backend.mcp_server import get_stock_price, research_stock

# Get stock price
result = get_stock_price("AAPL")
print(result["current_price"])  # 175.43

# Run full research
result = research_stock("How is Apple doing?")
print(result["text_report"])  # Full research report
```

### REST API

```bash
# Create research job
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "How is Apple doing?"}'

# Get result
curl http://localhost:8000/api/research/{job_id}
```
