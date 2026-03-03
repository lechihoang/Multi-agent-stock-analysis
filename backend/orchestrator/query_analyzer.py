import logging
from typing import List, Optional
from pydantic import BaseModel

from backend.tools.ticker_lookup import lookup_ticker
from backend.tools.entity_extraction import extract_company_name

logger = logging.getLogger(__name__)


_AGENTS = ["price", "financial", "news", "market", "sentiment", "risk"]


class QueryIntent(BaseModel):
    original_query: str
    ticker: str
    agents_needed: List[str]


class QueryAnalyzer:
    def analyze(self, query: str) -> QueryIntent:
        query_clean = query.strip()

        ticker = self.extract_ticker(query_clean)
        if not ticker:
            raise ValueError(f"Could not find ticker for query: {query}")

        logger.info(f"Query analyzed: ticker={ticker}, agents={_AGENTS}")

        return QueryIntent(
            original_query=query,
            ticker=ticker,
            agents_needed=_AGENTS,
        )

    def extract_ticker(self, query: str) -> Optional[str]:
        company_name = extract_company_name(query)

        if not company_name:
            logger.warning(f"LLM could not extract company name from: '{query}'")
            return None

        logger.info(f"LLM extracted company: '{company_name}' from query: '{query}'")

        ticker = lookup_ticker(company_name)

        if not ticker:
            logger.warning(f"Yahoo Finance could not find ticker for: '{company_name}'")
            return None

        logger.info(f"Yahoo Finance found ticker: '{ticker}' for company: '{company_name}'")
        return ticker
