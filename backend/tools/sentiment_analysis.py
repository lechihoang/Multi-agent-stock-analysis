from crewai.tools import tool
from typing import List

from backend.models.outputs import (
    StockSentimentResponse,
    SentimentSource,
    SocialMentionsResponse,
    SearchResult,
)
from backend.tools.utils import get_tavily_client


def search_sentiment(query: str, max_results: int = 10) -> dict:
    try:
        client = get_tavily_client()
        results = client.search(
            query=query,
            max_results=max_results,
            include_answer=True,
            include_raw_content=False,
            include_images=False,
        )
        return {
            "success": True,
            "results": results.get("results", []),
            "answer": results.get("answer", ""),
            "query": query,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "query": query}


def parse_results_to_search_results(results: list, max_items: int = 3) -> List[SearchResult]:
    search_results: List[SearchResult] = []
    for item in results[:max_items]:
        content = item.get("content", "")[:200] + "..." if item.get("content") else ""
        search_results.append(
            SearchResult(
                title=item.get("title", "No title"),
                url=item.get("url", ""),
                content=content,
                score=item.get("score"),
            )
        )
    return search_results


def analyze_stock_sentiment_core(ticker: str) -> StockSentimentResponse:
    try:
        sources: List[SentimentSource] = []
        trending_topics: List[str] = []

        reddit_query = f"{ticker} stock reddit sentiment analysis wallstreetbets"
        reddit_results = search_sentiment(reddit_query, max_results=5)

        if reddit_results["success"]:
            sources.append(
                SentimentSource(
                    source="reddit",
                    summary=reddit_results.get("answer", "")[:500]
                    if reddit_results.get("answer")
                    else None,
                    items=parse_results_to_search_results(reddit_results["results"]),
                )
            )

        twitter_query = f"{ticker} stock twitter sentiment trending"
        twitter_results = search_sentiment(twitter_query, max_results=5)

        if twitter_results["success"]:
            sources.append(
                SentimentSource(
                    source="twitter",
                    summary=twitter_results.get("answer", "")[:500]
                    if twitter_results.get("answer")
                    else None,
                    items=parse_results_to_search_results(twitter_results["results"]),
                )
            )

        news_query = f"{ticker} stock investor sentiment bullish bearish analysis"
        news_results = search_sentiment(news_query, max_results=5)

        if news_results["success"]:
            sources.append(
                SentimentSource(
                    source="news",
                    summary=news_results.get("answer", "")[:500]
                    if news_results.get("answer")
                    else None,
                    items=parse_results_to_search_results(news_results["results"]),
                )
            )

        trending_query = f"{ticker} stock trending topics discussions 2024"
        trending_results = search_sentiment(trending_query, max_results=5)

        if trending_results["success"]:
            for item in trending_results["results"][:3]:
                title = item.get("title", "")
                if title:
                    trending_topics.append(title)

        return StockSentimentResponse(
            success=True,
            ticker=ticker.upper(),
            sources=sources,
            trending_topics=trending_topics,
        )

    except Exception as e:
        return StockSentimentResponse(
            success=False,
            ticker=ticker.upper(),
            error=str(e),
        )


def get_social_mentions_core(ticker: str, platform: str = "all") -> SocialMentionsResponse:
    try:
        reddit_mentions: List[SearchResult] = []
        twitter_mentions: List[SearchResult] = []

        if platform in ["reddit", "all"]:
            reddit_query = f"{ticker} stock reddit discussion DD analysis"
            results = search_sentiment(reddit_query, max_results=8)

            if results["success"]:
                for item in results["results"][:5]:
                    content = item.get("content", "")[:300] + "..." if item.get("content") else ""
                    reddit_mentions.append(
                        SearchResult(
                            title=item.get("title", "No title"),
                            url=item.get("url", ""),
                            content=content,
                            score=item.get("score"),
                        )
                    )

        if platform in ["twitter", "all"]:
            twitter_query = f"{ticker} stock twitter cashtag discussion"
            results = search_sentiment(twitter_query, max_results=8)

            if results["success"]:
                for item in results["results"][:5]:
                    content = item.get("content", "")[:300] + "..." if item.get("content") else ""
                    twitter_mentions.append(
                        SearchResult(
                            title=item.get("title", "No title"),
                            url=item.get("url", ""),
                            content=content,
                            score=item.get("score"),
                        )
                    )

        return SocialMentionsResponse(
            success=True,
            ticker=ticker.upper(),
            platform=platform,
            reddit_mentions=reddit_mentions,
            twitter_mentions=twitter_mentions,
        )

    except Exception as e:
        return SocialMentionsResponse(
            success=False,
            ticker=ticker.upper(),
            platform=platform,
            error=str(e),
        )


@tool("Analyze Stock Sentiment")
def analyze_stock_sentiment(ticker: str) -> StockSentimentResponse:
    """Analyze stock sentiment from news and social media."""
    return analyze_stock_sentiment_core(ticker)


@tool("Get Social Media Mentions")
def get_social_mentions(ticker: str, platform: str = "all") -> SocialMentionsResponse:
    """Get social media mentions for a stock."""
    return get_social_mentions_core(ticker, platform)
