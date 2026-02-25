from crewai import LLM
from typing import Optional

from backend.config.settings import settings


def get_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> LLM:
    return LLM(
        model=model or settings.crewai_model,
        temperature=temperature or settings.llm_temperature,
        max_tokens=max_tokens or settings.llm_max_tokens,
        top_p=settings.llm_top_p,
        api_key=settings.nvidia_api_key,
    )


__all__ = ["get_llm"]
