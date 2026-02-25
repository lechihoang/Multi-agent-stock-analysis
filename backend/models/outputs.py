from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from enum import Enum
import re
class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    BULLISH = "bullish"
    BEARISH = "bearish"
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value == value_lower:
                    return member
            aliases = {
                "bullish": cls.POSITIVE,
                "bearish": cls.NEGATIVE,
                "very bullish": cls.POSITIVE,
                "very bearish": cls.NEGATIVE,
                "slightly bullish": cls.POSITIVE,
                "slightly bearish": cls.NEGATIVE,
                "moderately bullish": cls.POSITIVE,
                "moderately bearish": cls.NEGATIVE,
                "cautious bullish": cls.POSITIVE,
                "cautious": cls.NEUTRAL,
            }
            if value_lower in aliases:
                return aliases[value_lower]
        return None
class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
class TrendDirection(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    MIXED = "mixed"
class PriceData(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    current_price: Optional[float] = Field(None, description="Current stock price")
    currency: str = Field(default="USD", description="Currency of the price")
    day_high: Optional[float] = Field(None, description="Day's highest price")
    day_low: Optional[float] = Field(None, description="Day's lowest price")
    day_open: Optional[float] = Field(None, description="Day's opening price")
    previous_close: Optional[float] = Field(None, description="Previous closing price")
    volume: Optional[int] = Field(None, description="Trading volume")
    avg_volume: Optional[int] = Field(None, description="Average trading volume")
    week_52_high: Optional[float] = Field(None, description="52-week high")
    week_52_low: Optional[float] = Field(None, description="52-week low")
    daily_change: Optional[float] = Field(None, description="Daily price change")
    daily_change_percent: Optional[float] = Field(None, description="Daily change percentage")
    weekly_change_percent: Optional[float] = Field(None, description="Weekly change percentage")
    monthly_change_percent: Optional[float] = Field(None, description="Monthly change percentage")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())
    price_summary: Optional[str] = Field(
        None, description="Brief summary of current price situation"
    )
    @field_validator(
        "current_price",
        "day_high",
        "day_low",
        "day_open",
        "previous_close",
        "week_52_high",
        "week_52_low",
        "daily_change",
        "daily_change_percent",
        "weekly_change_percent",
        "monthly_change_percent",
        "market_cap",
        mode="before",
    )
    @classmethod
    def parse_float_fields(cls, v):
        return parse_float_or_none(v)
    @field_validator("volume", "avg_volume", mode="before")
    @classmethod
    def parse_int_fields(cls, v):
        result = parse_float_or_none(v)
        return int(result) if result is not None else None
class FinancialMetrics(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    pe_ratio: Optional[float] = Field(None, description="Price-to-Earnings ratio")
    forward_pe: Optional[float] = Field(None, description="Forward P/E ratio")
    peg_ratio: Optional[float] = Field(None, description="PEG ratio")
    price_to_book: Optional[float] = Field(None, description="Price-to-Book ratio")
    price_to_sales: Optional[float] = Field(None, description="Price-to-Sales ratio")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    enterprise_value: Optional[float] = Field(None, description="Enterprise value")
    profit_margin: Optional[float] = Field(None, description="Profit margin percentage")
    operating_margin: Optional[float] = Field(None, description="Operating margin percentage")
    return_on_equity: Optional[float] = Field(None, description="Return on equity percentage")
    return_on_assets: Optional[float] = Field(None, description="Return on assets percentage")
    revenue_growth_yoy: Optional[float] = Field(None, description="Revenue growth year-over-year")
    earnings_growth_yoy: Optional[float] = Field(None, description="Earnings growth year-over-year")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield percentage")
    dividend_rate: Optional[float] = Field(None, description="Annual dividend rate")
    payout_ratio: Optional[float] = Field(None, description="Dividend payout ratio")
    debt_to_equity: Optional[float] = Field(None, description="Debt-to-equity ratio")
    current_ratio: Optional[float] = Field(None, description="Current ratio")
    quick_ratio: Optional[float] = Field(None, description="Quick ratio")
    financial_health: str = Field(..., description="Assessment of financial health")
    key_strengths: List[str] = Field(default_factory=list, description="Key financial strengths")
    key_concerns: List[str] = Field(default_factory=list, description="Key financial concerns")
    fiscal_period: Optional[str] = Field(None, description="Latest fiscal period reported")
    @field_validator("key_strengths", "key_concerns", mode="before")
    @classmethod
    def convert_none_to_list(cls, v):
        return v if v is not None else []
    @field_validator(
        "pe_ratio",
        "forward_pe",
        "peg_ratio",
        "price_to_book",
        "price_to_sales",
        "market_cap",
        "enterprise_value",
        "profit_margin",
        "operating_margin",
        "return_on_equity",
        "return_on_assets",
        "revenue_growth_yoy",
        "earnings_growth_yoy",
        "dividend_yield",
        "dividend_rate",
        "payout_ratio",
        "debt_to_equity",
        "current_ratio",
        "quick_ratio",
        mode="before",
    )
    @classmethod
    def parse_float_fields(cls, v):
        return parse_float_or_none(v)
class NewsItem(BaseModel):
    title: str = Field(..., description="News headline")
    source: str = Field(..., description="News source")
    published_date: Optional[str] = Field(None, description="Publication date")
    summary: str = Field(..., description="Brief summary of the news")
    sentiment: Sentiment = Field(default=Sentiment.NEUTRAL, description="Sentiment of the news")
    relevance: str = Field(default="medium", description="Relevance to stock performance")
class NewsAnalysis(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    recent_news: List[NewsItem] = Field(
        default_factory=list, description="List of recent news items"
    )
    analyst_ratings: Optional[str] = Field(None, description="Recent analyst rating changes")
    price_targets: Optional[str] = Field(None, description="Recent price target updates")
    upcoming_events: List[str] = Field(
        default_factory=list, description="Upcoming events/catalysts"
    )
    overall_sentiment: Sentiment = Field(default=Sentiment.NEUTRAL)
    sentiment_score: Optional[float] = Field(
        None, ge=-1, le=1, description="Sentiment score from -1 to 1"
    )
    key_themes: List[str] = Field(default_factory=list, description="Key themes in recent news")
    risk_signals: List[str] = Field(default_factory=list, description="Potential risk signals")
    opportunity_signals: List[str] = Field(
        default_factory=list, description="Potential opportunity signals"
    )
    news_summary: str = Field(..., description="Executive summary of news impact")
    @field_validator(
        "recent_news",
        "upcoming_events",
        "key_themes",
        "risk_signals",
        "opportunity_signals",
        mode="before",
    )
    @classmethod
    def convert_none_to_list(cls, v):
        return v if v is not None else []
class TechnicalIndicator(BaseModel):
    name: str = Field(..., description="Indicator name")
    value: Optional[float] = Field(None, description="Current value")
    @field_validator("value", mode="before")
    @classmethod
    def parse_value(cls, v):
        return parse_float_or_none(v)
def parse_float_or_none(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        match = re.search(r"[-+]?\d*\.?\d+", value.replace(",", ""))
        if match:
            try:
                return float(match.group())
            except (ValueError, TypeError):
                pass
    return None
class MarketTrends(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    performance_1m: Optional[float] = Field(None, description="1-month performance percentage")
    performance_3m: Optional[float] = Field(None, description="3-month performance percentage")
    performance_6m: Optional[float] = Field(None, description="6-month performance percentage")
    performance_1y: Optional[float] = Field(None, description="1-year performance percentage")
    performance_ytd: Optional[float] = Field(None, description="Year-to-date performance")
    vs_sp500: Optional[float] = Field(None, description="Performance vs S&P 500")
    vs_sector: Optional[float] = Field(None, description="Performance vs sector average")
    @field_validator(
        "performance_1m",
        "performance_3m",
        "performance_6m",
        "performance_1y",
        "performance_ytd",
        "vs_sp500",
        "vs_sector",
        mode="before",
    )
    @classmethod
    def parse_float_fields(cls, v):
        return parse_float_or_none(v)
    short_term_trend: TrendDirection = Field(default=TrendDirection.MIXED)
    medium_term_trend: TrendDirection = Field(default=TrendDirection.MIXED)
    long_term_trend: TrendDirection = Field(default=TrendDirection.MIXED)
    technical_indicators: List[TechnicalIndicator] = Field(default_factory=list)
    support_levels: List[float] = Field(default_factory=list, description="Key support levels")
    resistance_levels: List[float] = Field(
        default_factory=list, description="Key resistance levels"
    )
    volume_trend: str = Field(default="normal", description="Volume trend analysis")
    analyst_consensus: Optional[str] = Field(None, description="Analyst consensus rating")
    buy_count: Optional[int] = Field(None, description="Number of buy ratings")
    hold_count: Optional[int] = Field(None, description="Number of hold ratings")
    sell_count: Optional[int] = Field(None, description="Number of sell ratings")
    outlook_summary: str = Field(..., description="Market outlook summary")
    key_catalysts: List[str] = Field(default_factory=list, description="Key catalysts to watch")
    @field_validator(
        "technical_indicators",
        "support_levels",
        "resistance_levels",
        "key_catalysts",
        mode="before",
    )
    @classmethod
    def convert_none_to_list(cls, v):
        return v if v is not None else []
class SocialMentions(BaseModel):
    platform: str = Field(..., description="Social media platform (reddit/twitter/stocktwits)")
    mention_count: int = Field(default=0, description="Number of mentions")
    sentiment: Sentiment = Field(default=Sentiment.NEUTRAL, description="Platform sentiment")
    trending_topics: List[str] = Field(default_factory=list, description="Trending topics")
class SentimentData(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    overall_sentiment: Sentiment = Field(
        default=Sentiment.NEUTRAL, description="Overall market sentiment"
    )
    sentiment_score: float = Field(
        default=0.0, ge=-1.0, le=1.0, description="Sentiment score from -1 to 1"
    )
    social_mentions_24h: int = Field(default=0, description="Total social mentions in 24h")
    social_mentions_7d: int = Field(default=0, description="Total social mentions in 7 days")
    social_platforms: List[SocialMentions] = Field(
        default_factory=list, description="Breakdown by platform"
    )
    reddit_sentiment: Sentiment = Field(default=Sentiment.NEUTRAL, description="Reddit sentiment")
    twitter_sentiment: Sentiment = Field(
        default=Sentiment.NEUTRAL, description="Twitter/X sentiment"
    )
    news_sentiment: Sentiment = Field(default=Sentiment.NEUTRAL, description="News media sentiment")
    trending_topics: List[str] = Field(
        default_factory=list, description="Trending topics/hashtags related to stock"
    )
    sentiment_momentum: str = Field(
        default="stable", description="Sentiment trend: improving/stable/deteriorating"
    )
    sentiment_change_7d: Optional[float] = Field(None, description="Sentiment change over 7 days")
    bullish_signals: List[str] = Field(
        default_factory=list, description="Bullish signals from social/news"
    )
    bearish_signals: List[str] = Field(
        default_factory=list, description="Bearish signals from social/news"
    )
    key_discussions: List[str] = Field(default_factory=list, description="Key discussion points")
    risk_signals: List[str] = Field(default_factory=list, description="Risk signals detected")
    sentiment_summary: str = Field(..., description="Executive summary of sentiment analysis")
    @field_validator(
        "social_platforms",
        "trending_topics",
        "bullish_signals",
        "bearish_signals",
        "key_discussions",
        "risk_signals",
        mode="before",
    )
    @classmethod
    def convert_none_to_list(cls, v):
        return v if v is not None else []
    @field_validator("sentiment_score", "sentiment_change_7d", mode="before")
    @classmethod
    def parse_float_fields(cls, v):
        result = parse_float_or_none(v)
        return result if result is not None else 0.0
    @field_validator("social_mentions_24h", "social_mentions_7d", mode="before")
    @classmethod
    def parse_int_fields(cls, v):
        result = parse_float_or_none(v)
        return int(result) if result is not None else 0
class RiskAssessment(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    var_95_daily: Optional[float] = Field(
        None, description="95% Value at Risk (daily, as percentage)"
    )
    var_99_daily: Optional[float] = Field(
        None, description="99% Value at Risk (daily, as percentage)"
    )
    cvar_95: Optional[float] = Field(None, description="Conditional VaR (Expected Shortfall) 95%")
    historical_volatility_30d: Optional[float] = Field(
        None, description="30-day historical volatility (annualized)"
    )
    historical_volatility_90d: Optional[float] = Field(
        None, description="90-day historical volatility (annualized)"
    )
    volatility_percentile: Optional[float] = Field(
        None, description="Current volatility percentile vs history"
    )
    beta: Optional[float] = Field(None, description="Beta vs S&P 500")
    beta_sector: Optional[float] = Field(None, description="Beta vs sector ETF")
    r_squared: Optional[float] = Field(None, description="R-squared (systematic risk proportion)")
    max_drawdown_1y: Optional[float] = Field(None, description="Maximum drawdown in last 1 year")
    max_drawdown_3y: Optional[float] = Field(None, description="Maximum drawdown in last 3 years")
    current_drawdown: Optional[float] = Field(None, description="Current drawdown from peak")
    avg_recovery_days: Optional[int] = Field(
        None, description="Average days to recover from drawdowns"
    )
    sharpe_ratio: Optional[float] = Field(
        None, description="Sharpe ratio (risk-free rate assumed 5%)"
    )
    sortino_ratio: Optional[float] = Field(None, description="Sortino ratio (downside deviation)")
    skewness: Optional[float] = Field(None, description="Return distribution skewness")
    kurtosis: Optional[float] = Field(None, description="Return distribution kurtosis")
    tail_risk_score: str = Field(
        default="moderate", description="Tail risk assessment: low/moderate/high"
    )
    correlation_sp500: Optional[float] = Field(None, description="Correlation with S&P 500")
    correlation_nasdaq: Optional[float] = Field(None, description="Correlation with NASDAQ")
    correlation_sector: Optional[float] = Field(None, description="Correlation with sector ETF")
    risk_level: RiskLevel = Field(default=RiskLevel.MODERATE, description="Overall risk level")
    risk_score: Optional[float] = Field(None, ge=0, le=100, description="Risk score 0-100")
    key_risks: List[str] = Field(default_factory=list, description="Key risk factors")
    risk_mitigants: List[str] = Field(default_factory=list, description="Potential risk mitigants")
    @field_validator("key_risks", "risk_mitigants", mode="before")
    @classmethod
    def convert_none_to_list(cls, v):
        return v if v is not None else []
    position_sizing_suggestion: Optional[str] = Field(
        None, description="Suggested position size based on risk"
    )
    stop_loss_suggestion: Optional[float] = Field(
        None, description="Suggested stop-loss percentage"
    )
    risk_summary: str = Field(..., description="Executive summary of risk analysis")
    @field_validator(
        "var_95_daily",
        "var_99_daily",
        "cvar_95",
        "historical_volatility_30d",
        "historical_volatility_90d",
        "volatility_percentile",
        "beta",
        "beta_sector",
        "r_squared",
        "max_drawdown_1y",
        "max_drawdown_3y",
        "current_drawdown",
        "sharpe_ratio",
        "sortino_ratio",
        "skewness",
        "kurtosis",
        "correlation_sp500",
        "correlation_nasdaq",
        "correlation_sector",
        "risk_score",
        "stop_loss_suggestion",
        mode="before",
    )
    @classmethod
    def parse_float_fields(cls, v):
        return parse_float_or_none(v)
    @field_validator("avg_recovery_days", mode="before")
    @classmethod
    def parse_int_fields(cls, v):
        result = parse_float_or_none(v)
        return int(result) if result is not None else None
class InvestmentOutlook(str, Enum):
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"
class ResearchReport(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    report_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    executive_summary: str = Field(..., description="2-3 sentence executive summary")
    current_price: Optional[float] = Field(None, description="Current stock price")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    pe_ratio: Optional[float] = Field(None, description="P/E ratio")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield")
    price_analysis_summary: str = Field(..., description="Summary of price analysis")
    financial_analysis_summary: str = Field(..., description="Summary of financial analysis")
    news_analysis_summary: str = Field(..., description="Summary of news analysis")
    market_analysis_summary: str = Field(..., description="Summary of market trend analysis")
    sentiment_analysis_summary: Optional[str] = Field(
        None, description="Summary of sentiment analysis"
    )
    risk_analysis_summary: Optional[str] = Field(None, description="Summary of risk analysis")
    investment_outlook: InvestmentOutlook = Field(default=InvestmentOutlook.NEUTRAL)
    outlook_rationale: str = Field(..., description="Rationale for the investment outlook")
    risk_factors: List[str] = Field(default_factory=list, description="Key risk factors")
    risk_level: RiskLevel = Field(default=RiskLevel.MODERATE)
    opportunities: List[str] = Field(default_factory=list, description="Key opportunities")
    recommendation: str = Field(..., description="Investment recommendation")
    price_target: Optional[float] = Field(None, description="Price target if available")
    suitable_for: List[str] = Field(default_factory=list, description="Suitable investor types")
    time_horizon: Optional[str] = Field(None, description="Recommended time horizon")
    data_sources: List[str] = Field(default_factory=list, description="Sources used")
    disclaimer: str = Field(
        default="This report is for informational purposes only and does not constitute investment advice.",
        description="Standard disclaimer",
    )
    @field_validator("risk_factors", "opportunities", "suitable_for", "data_sources", mode="before")
    @classmethod
    def convert_none_to_list(cls, v):
        return v if v is not None else []
    @field_validator(
        "current_price",
        "market_cap",
        "pe_ratio",
        "dividend_yield",
        "price_target",
        mode="before",
    )
    @classmethod
    def parse_float_fields(cls, v):
        return parse_float_or_none(v)
AgentOutput = (
    PriceData
    | FinancialMetrics
    | NewsAnalysis
    | MarketTrends
    | SentimentData
    | RiskAssessment
    | ResearchReport
)
class StockFinancialsResponse(BaseModel):
    success: bool = True
    ticker: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    employees: Optional[int] = None
    business_summary: Optional[str] = None
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    day_open: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    volume_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    profit_margin: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    revenue: Optional[float] = None
    revenue_per_share: Optional[float] = None
    dividend_rate: Optional[float] = None
    dividend_yield: Optional[float] = None
    ex_dividend_date: Optional[str] = None
    payout_ratio: Optional[float] = None
    total_debt: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    recommendation: Optional[str] = None
    target_mean_price: Optional[float] = None
    target_high_price: Optional[float] = None
    target_low_price: Optional[int] = None
    num_analysts: Optional[int] = None
    error: Optional[str] = None
class PriceHistoryDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
class PriceHistoryStatistics(BaseModel):
    start_date: str
    end_date: str
    data_points: int
    avg_close: float
    min_close: float
    max_close: float
    total_volume: int
    avg_volume: int
class StockPriceHistoryResponse(BaseModel):
    success: bool = True
    ticker: str
    period: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    recent_prices: List[PriceHistoryDataPoint] = Field(default_factory=list)
    statistics: Optional[PriceHistoryStatistics] = None
    error: Optional[str] = None
class RiskMetricsResponse(BaseModel):
    success: bool = True
    ticker: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    beta: Optional[float] = None
    beta_3_year: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    error: Optional[str] = None
class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: Optional[float] = None
class TavilySearchResponse(BaseModel):
    success: bool = True
    query: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    answer: Optional[str] = None
    results: List[SearchResult] = Field(default_factory=list)
    result_count: int = 0
    error: Optional[str] = None
class SentimentSource(BaseModel):
    source: str  
    summary: Optional[str] = None
    items: List[SearchResult] = Field(default_factory=list)
class StockSentimentResponse(BaseModel):
    success: bool = True
    ticker: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    sources: List[SentimentSource] = Field(default_factory=list)
    trending_topics: List[str] = Field(default_factory=list)
    error: Optional[str] = None
class SocialMentionsResponse(BaseModel):
    success: bool = True
    ticker: str
    platform: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    reddit_mentions: List[SearchResult] = Field(default_factory=list)
    twitter_mentions: List[SearchResult] = Field(default_factory=list)
    error: Optional[str] = None