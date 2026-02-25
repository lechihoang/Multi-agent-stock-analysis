import os
import sys
import logging
from typing import Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from backend.tools.tavily_search import search_tavily_core
from backend.tools.utils import get_tavily_client

from backend.tools.sentiment_analysis import (
    analyze_stock_sentiment_core,
    get_social_mentions_core,
)
from backend.tools.risk_analysis import (
    calculate_risk_metrics_core,
)
from backend.tools.stock_data import (
    get_stock_price_core,
    get_financial_metrics_core,
    get_stock_financials_core,
    get_stock_price_history_core,
)
from backend.tools.entity_extraction import extract_company_name_core
from backend.tools.ticker_lookup import lookup_ticker_core

from backend.orchestrator.mcp_orchestrator import MCPOrchestrator
from backend.orchestrator.query_analyzer import QueryAnalyzer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

mcp = FastMCP("stock_research")


@mcp.tool(
    name="stock_research",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)
def research_stock(query: str) -> dict:
    logger.info(f"MCP Tool: research_stock called with query: {query}")

    try:
        orchestrator = MCPOrchestrator()
        result = orchestrator.execute_sync(query)

        if result.success:
            return {
                "success": True,
                "ticker": result.ticker,
                "query_type": result.query_type.value,
                "report": result.structured_report.model_dump(),
                "text_report": result.final_report,
                "execution_time_seconds": result.total_execution_time,
                "agents_executed": [r.agent_name for r in result.agent_results],
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "success": False,
                "error": result.error,
                "ticker": result.ticker if result.ticker else "Unknown",
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"research_stock error: {str(e)}")
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}


@mcp.tool(
    name="stock_get_price",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def get_stock_price(ticker: str) -> dict:
    logger.info(f"MCP Tool: get_stock_price called for {ticker}")
    return get_stock_price_core(ticker)


@mcp.tool(
    name="stock_get_financial_metrics",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def get_financial_metrics(ticker: str) -> dict:
    logger.info(f"MCP Tool: get_financial_metrics called for {ticker}")
    return get_financial_metrics_core(ticker)


@mcp.tool(
    name="stock_search_news",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def search_financial_news(query: str, max_results: int = 10) -> dict:
    logger.info(f"MCP Tool: search_financial_news called with query: {query}")

    try:
        result = search_tavily_core(query=query, max_results=max_results)

        if result.success:
            return {
                "success": True,
                "query": query,
                "answer": result.answer,
                "results": [
                    {
                        "title": item.title,
                        "url": item.url,
                        "content": item.content[:500] if item.content else "",
                        "score": item.score,
                    }
                    for item in result.results
                ],
                "result_count": result.result_count,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "success": False,
                "query": query,
                "error": result.error,
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"search_financial_news error: {str(e)}")
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@mcp.tool(
    name="stock_analyze_sentiment",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def analyze_sentiment(ticker: str) -> dict:
    logger.info(f"MCP Tool: analyze_sentiment called for {ticker}")

    try:
        sentiment_result = analyze_stock_sentiment_core(ticker)
        social_result = get_social_mentions_core(ticker)

        return {
            "success": True,
            "ticker": ticker.upper(),
            "sentiment_analysis": sentiment_result.model_dump(),
            "social_mentions": social_result.model_dump(),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"analyze_sentiment error: {str(e)}")
        return {
            "success": False,
            "ticker": ticker.upper(),
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@mcp.tool(
    name="stock_analyze_risk",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def analyze_risk(ticker: str) -> dict:
    logger.info(f"MCP Tool: analyze_risk called for {ticker}")

    try:
        risk_result = calculate_risk_metrics_core(ticker)

        return {
            "success": True,
            "ticker": ticker.upper(),
            "risk_metrics": risk_result.model_dump(),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"analyze_risk error: {str(e)}")
        return {
            "success": False,
            "ticker": ticker.upper(),
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@mcp.tool(
    name="stock_get_price_history",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def get_price_history(ticker: str, period: str = "1y") -> dict:
    logger.info(f"MCP Tool: get_price_history called for {ticker}, period={period}")

    try:
        result = get_stock_price_history_core(ticker, period)

        if result.success:
            return {
                "success": True,
                "ticker": ticker.upper(),
                "period": period,
                "data_points": result.statistics.data_points if result.statistics else 0,
                "start_date": result.statistics.start_date if result.statistics else "",
                "end_date": result.statistics.end_date if result.statistics else "",
                "recent_prices": [
                    {
                        "date": p.date,
                        "open": p.open,
                        "high": p.high,
                        "low": p.low,
                        "close": p.close,
                        "volume": p.volume,
                    }
                    for p in result.recent_prices
                ],
                "statistics": {
                    "avg_close": result.statistics.avg_close if result.statistics else None,
                    "min_close": result.statistics.min_close if result.statistics else None,
                    "max_close": result.statistics.max_close if result.statistics else None,
                    "total_volume": result.statistics.total_volume if result.statistics else None,
                    "avg_volume": result.statistics.avg_volume if result.statistics else None,
                },
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "success": False,
                "ticker": ticker.upper(),
                "error": result.error,
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"get_price_history error: {str(e)}")
        return {
            "success": False,
            "ticker": ticker.upper(),
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@mcp.tool(
    name="stock_parse_query",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def parse_stock_query(query: str) -> dict:
    logger.info(f"MCP Tool: parse_stock_query called with: {query}")

    try:
        analyzer = QueryAnalyzer()
        intent = analyzer.analyze(query)

        return {
            "success": True,
            "original_query": query,
            "ticker": intent.ticker,
            "query_type": intent.query_type.value,
            "agents_needed": intent.agents_needed,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"parse_stock_query error: {str(e)}")
        return {
            "success": False,
            "original_query": query,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@mcp.tool(
    name="stock_extract_company",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def extract_company(query: str) -> dict:
    logger.info(f"MCP Tool: extract_company called with query: {query}")

    try:
        result = extract_company_name_core(query)
        return {
            "success": True,
            "original_query": query,
            "company_name": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"extract_company error: {str(e)}")
        return {
            "success": False,
            "original_query": query,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@mcp.tool(
    name="stock_lookup_ticker",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def lookup_ticker(query: str) -> dict:
    logger.info(f"MCP Tool: lookup_ticker called with query: {query}")

    try:
        result = lookup_ticker_core(query)
        return {
            "success": True,
            "original_query": query,
            "ticker": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"lookup_ticker error: {str(e)}")
        return {
            "success": False,
            "original_query": query,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@mcp.resource("stock://{ticker}/profile")
def get_company_profile(ticker: str) -> str:
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker)
        info = stock.info

        return f"""
Company Profile: {info.get("shortName", ticker.upper())}
Ticker: {ticker.upper()}
Sector: {info.get("sector", "N/A")}
Industry: {info.get("industry", "N/A")}
Country: {info.get("country", "N/A")}
Website: {info.get("website", "N/A")}
Employees: {info.get("fullTimeEmployees", "N/A")}

Business Summary:
{info.get("longBusinessSummary", "No description available.")}
"""
    except Exception as e:
        return f"Error fetching profile for {ticker}: {str(e)}"


@mcp.resource("stock://{ticker}/summary")
def get_stock_summary(ticker: str) -> str:
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = info.get("currentPrice") or info.get("regularMarketPrice", "N/A")
        market_cap = info.get("marketCap", 0)
        market_cap_str = f"${market_cap / 1e9:.2f}B" if market_cap else "N/A"

        return f"""
{info.get("shortName", ticker.upper())} ({ticker.upper()})
Current Price: ${current_price}
Market Cap: {market_cap_str}
P/E Ratio: {info.get("trailingPE", "N/A")}
52W Range: ${info.get("fiftyTwoWeekLow", "N/A")} - ${info.get("fiftyTwoWeekHigh", "N/A")}
Analyst Rating: {info.get("recommendationKey", "N/A")}
"""
    except Exception as e:
        return f"Error fetching summary for {ticker}: {str(e)}"


@mcp.prompt()
def stock_research_prompt(ticker: str) -> str:
    return f"""
You are a financial analyst researching {ticker.upper()}.

Please provide a comprehensive analysis covering:
1. Current stock price and recent performance
2. Key financial metrics and valuation
3. Recent news and market developments
4. Technical analysis and trends
5. Risk assessment
6. Investment recommendation

Use the available MCP tools to gather data:
- get_stock_price({ticker}) for current price
- get_financial_metrics({ticker}) for fundamentals
- search_financial_news("{ticker} stock news") for recent news
- analyze_risk({ticker}) for risk metrics
- analyze_sentiment({ticker}) for market sentiment

Synthesize the data into a clear, actionable research report.
"""


@mcp.prompt()
def quick_price_check_prompt(ticker: str) -> str:
    return f"""
Get the current stock price and key metrics for {ticker.upper()}.

Use get_stock_price({ticker}) and provide:
- Current price and daily change
- Trading volume vs average
- Position within 52-week range
- Brief assessment of current momentum
"""


@mcp.prompt()
def risk_analysis_prompt(ticker: str) -> str:
    return f"""
Perform a comprehensive risk analysis for {ticker.upper()}.

Use analyze_risk({ticker}) and provide:
- Value at Risk (VaR) interpretation
- Beta and market correlation analysis
- Volatility regime assessment
- Maximum drawdown history
- Position sizing recommendations
- Key risk factors to monitor
"""


def main():
    logger.info("Starting Stock Research MCP Server v2.0.0")
    logger.info("Protocol: Model Context Protocol (JSON-RPC 2.0)")
    logger.info("Available tools: research_stock, get_stock_price, get_financial_metrics, etc.")

    mcp.run()


if __name__ == "__main__":
    main()
