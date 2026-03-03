import logging
from typing import Optional
from functools import lru_cache

from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from crewai.tools import tool

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class CompanyExtraction(BaseModel):
    company_name: str = Field(
        description="The company name or stock ticker extracted from the query"
    )
    confidence: str = Field(description="Confidence level: high, medium, or low")
    reasoning: str = Field(description="Brief explanation of how the company name was identified")


def get_instructor_client():
    client = OpenAI(
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key,
    )
    return instructor.from_openai(client)


def extract_company_name_core(query: str) -> Optional[str]:
    if not query or not query.strip():
        return None

    try:
        client = get_instructor_client()

        result = client.chat.completions.create(
            model=settings.openai_model,
            response_model=CompanyExtraction,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst. Given the company name provided by user, return the exact company name. The user may enter a company name in any format (full name, common name, or partial name). Extract and normalize the company name.",
                },
                {
                    "role": "user",
                    "content": f"Extract the company name from this query: {query.strip()}",
                },
            ],
            temperature=0.1,
        )

        company_name = result.company_name.strip()

        if company_name and company_name.lower() not in ["none", "null", "n/a", ""]:
            logger.info(
                f"LLM extracted company: '{company_name}' (confidence: {result.confidence}) "
                f"from query: '{query}'"
            )
            return company_name
        else:
            logger.warning(f"LLM returned empty company name for query: '{query}'")
            return None

    except Exception as e:
        logger.error(f"Error extracting entity with LLM: {e}")
        return None


@lru_cache(maxsize=128)
def extract_company_name(query: str) -> Optional[str]:
    return extract_company_name_core(query)
