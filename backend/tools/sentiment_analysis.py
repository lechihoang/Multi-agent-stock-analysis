from crewai.tools import tool
from typing import List

from backend.models.outputs import (
    StockSentimentResponse,
    SentimentSource,
    SocialMentionsResponse,
    SearchResult,
)
from backend.tools.tavily_search import search_tavily


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
        reddit_results = search_tavily(reddit_query, max_results=5)

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
        twitter_results = search_tavily(twitter_query, max_results=5)

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
        news_results = search_tavily(news_query, max_results=5)

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
        trending_results = search_tavily(trending_query, max_results=5)

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
            results = search_tavily(reddit_query, max_results=8)

            if results["success"]:
                reddit_mentions = parse_results_to_search_results(results["results"], max_items=5)

        if platform in ["twitter", "all"]:
            twitter_query = f"{ticker} stock twitter cashtag discussion"
            results = search_tavily(twitter_query, max_results=8)

            if results["success"]:
                twitter_mentions = parse_results_to_search_results(results["results"], max_items=5)

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
