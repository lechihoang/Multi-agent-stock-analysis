from crewai.tools import tool
from typing import List

from backend.models.outputs import (
    TavilySearchResponse,
    SearchResult,
)
from backend.tools.utils import get_tavily_client


def search_tavily_core(query: str, max_results: int = 10) -> TavilySearchResponse:
    try:
        client = get_tavily_client()
        result = client.search(
            query=query,
            max_results=max_results,
            include_answer=True,
            include_raw_content=False,
            include_images=False,
        )

        if not result.get("success", True) and "results" not in result:
            return TavilySearchResponse(
                success=False,
                query=query,
                error=result.get("error", "Search failed"),
            )

        search_results: List[SearchResult] = []
        for item in result.get("results", [])[:10]:
            content = item.get("content", "")
            if len(content) > 300:
                content = content[:300] + "..."
            search_results.append(
                SearchResult(
                    title=item.get("title", "No title"),
                    url=item.get("url", ""),
                    content=content,
                    score=item.get("score"),
                )
            )

        return TavilySearchResponse(
            success=True,
            query=query,
            answer=result.get("answer"),
            results=search_results,
            result_count=len(search_results),
        )

    except Exception as e:
        return TavilySearchResponse(
            success=False,
            query=query,
            error=str(e),
        )


def search_tavily(query: str, max_results: int = 10) -> dict:
    response = search_tavily_core(query, max_results)
    return {
        "success": response.success,
        "results": [
            {"title": r.title, "url": r.url, "content": r.content, "score": r.score}
            for r in response.results
        ],
        "answer": response.answer,
        "query": response.query,
        "error": response.error,
    }


@tool("Tavily Search")
def tavily_search(query: str) -> TavilySearchResponse:
    """Search for news and information using Tavily."""
    return search_tavily_core(query=query, max_results=10)
