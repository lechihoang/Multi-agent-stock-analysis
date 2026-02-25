from typing import Optional
import pandas as pd
import os

from tavily import TavilyClient


_tavily_client = None


def safe_float(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if pd.isna(value):
            return None
        return float(value)
    return None


def safe_int(value) -> Optional[int]:
    result = safe_float(value)
    return int(result) if result is not None else None


def get_tavily_client() -> TavilyClient:
    global _tavily_client
    if _tavily_client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


__all__ = [
    "safe_float",
    "safe_int",
    "get_tavily_client",
]
