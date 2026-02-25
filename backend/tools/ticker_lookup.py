import yfinance as yf
from typing import Optional
from functools import lru_cache
import logging
from crewai.tools import tool

logger = logging.getLogger(__name__)


def lookup_ticker_core(query: str) -> Optional[str]:
    query = query.strip()

    if not query:
        return None

    try:
        search = yf.Search(query, max_results=10)
        quotes = search.quotes

        if not quotes:
            logger.warning(f"No results found for query: '{query}'")
            return None

        for quote in quotes:
            quote_type = quote.get("quoteType", "").upper()
            if quote_type == "EQUITY":
                symbol = quote.get("symbol")
                if symbol:
                    logger.info(f"Found ticker '{symbol}' for query '{query}'")
                    return symbol

        first_quote = quotes[0]
        symbol = first_quote.get("symbol")
        if symbol:
            logger.info(f"Found ticker '{symbol}' (non-equity) for query '{query}'")
            return symbol

        return None

    except Exception as e:
        logger.error(f"Error looking up ticker for '{query}': {e}")
        return None


@lru_cache(maxsize=256)
def lookup_ticker(query: str) -> Optional[str]:
    return lookup_ticker_core(query)


@tool("Lookup Stock Ticker")
def lookup_ticker_tool(query: str) -> str:
    """Lookup stock ticker from company name."""
    result = lookup_ticker_core(query)
    return result if result else f"Could not find ticker for: {query}"
