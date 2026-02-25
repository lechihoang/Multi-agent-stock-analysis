from crewai.tools import tool
import yfinance as yf
from datetime import datetime

from backend.models.outputs import (
    StockFinancialsResponse,
    StockPriceHistoryResponse,
    PriceHistoryDataPoint,
    PriceData,
)

from backend.tools.utils import safe_float, safe_int


def get_stock_price_data(ticker: str) -> PriceData:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
        day_high = safe_float(info.get("dayHigh"))
        day_low = safe_float(info.get("dayLow"))

        if current_price is None:
            return PriceData(
                ticker=ticker.upper(),
                current_price=None,
                day_high=None,
                day_low=None,
                price_summary=f"Unable to fetch price data for {ticker}",
            )

        previous_close = safe_float(info.get("previousClose"))
        daily_change = None
        daily_change_percent = None
        if previous_close:
            daily_change = current_price - previous_close
            daily_change_percent = (daily_change / previous_close) * 100

        volume = safe_int(info.get("volume"))
        avg_volume = safe_int(info.get("averageVolume"))
        week_52_high = safe_float(info.get("fiftyTwoWeekHigh"))
        week_52_low = safe_float(info.get("fiftyTwoWeekLow"))
        market_cap = safe_float(info.get("marketCap"))

        summary = f"{ticker.upper()} is currently trading at ${current_price:.2f}"
        if daily_change:
            direction = "up" if daily_change > 0 else "down"
            summary += f", {direction} ${abs(daily_change):.2f} ({daily_change_percent:.2f}%)"
        if week_52_high and week_52_low:
            summary += f". 52-week range: ${week_52_low:.2f} - ${week_52_high:.2f}"

        return PriceData(
            ticker=ticker.upper(),
            current_price=current_price,
            day_high=day_high,
            day_low=day_low,
            day_open=safe_float(info.get("open")),
            previous_close=previous_close,
            volume=volume,
            avg_volume=avg_volume,
            week_52_high=week_52_high,
            week_52_low=week_52_low,
            daily_change=daily_change,
            daily_change_percent=daily_change_percent,
            market_cap=market_cap,
            price_summary=summary,
        )

    except Exception as e:
        return PriceData(
            ticker=ticker.upper(),
            current_price=None,
            day_high=None,
            day_low=None,
            price_summary=f"Error fetching price data: {str(e)}",
        )


@tool("Get Stock Price Data")
def get_stock_price(ticker: str) -> PriceData:
    """Get current stock price data."""
    return get_stock_price_data(ticker)


def get_stock_price_core(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        previous_close = info.get("previousClose")

        change = None
        change_percent = None
        if current_price and previous_close:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100

        return {
            "success": True,
            "ticker": ticker.upper(),
            "current_price": current_price,
            "previous_close": previous_close,
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "day_open": info.get("open"),
            "volume": info.get("volume"),
            "avg_volume": info.get("averageVolume"),
            "market_cap": info.get("marketCap"),
            "week_52_high": info.get("fiftyTwoWeekHigh"),
            "week_52_low": info.get("fiftyTwoWeekLow"),
            "change": change,
            "change_percent": change_percent,
            "currency": info.get("currency", "USD"),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "success": False,
            "ticker": ticker.upper(),
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def get_financial_metrics_core(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "success": True,
            "ticker": ticker.upper(),
            "company_name": info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "enterprise_value": info.get("enterpriseValue"),
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "gross_margin": info.get("grossMargins"),
            "return_on_equity": info.get("returnOnEquity"),
            "return_on_assets": info.get("returnOnAssets"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "revenue": info.get("totalRevenue"),
            "earnings_per_share": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "dividend_rate": info.get("dividendRate"),
            "payout_ratio": info.get("payoutRatio"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "total_debt": info.get("totalDebt"),
            "recommendation": info.get("recommendationKey"),
            "target_mean_price": info.get("targetMeanPrice"),
            "number_of_analysts": info.get("numberOfAnalystOpinions"),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "success": False,
            "ticker": ticker.upper(),
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def get_stock_financials_core(ticker: str) -> StockFinancialsResponse:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        summary = info.get("longBusinessSummary", "")
        if summary and len(summary) > 500:
            summary = summary[:500] + "..."

        return StockFinancialsResponse(
            success=True,
            ticker=ticker.upper(),
            company_name=info.get("shortName"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            country=info.get("country"),
            website=info.get("website"),
            employees=safe_int(info.get("fullTimeEmployees")),
            business_summary=summary,
            current_price=safe_float(info.get("currentPrice") or info.get("regularMarketPrice")),
            previous_close=safe_float(info.get("previousClose")),
            day_open=safe_float(info.get("open")),
            day_high=safe_float(info.get("dayHigh")),
            day_low=safe_float(info.get("dayLow")),
            week_52_high=safe_float(info.get("fiftyTwoWeekHigh")),
            week_52_low=safe_float(info.get("fiftyTwoWeekLow")),
            volume=safe_int(info.get("volume")),
            avg_volume=safe_int(info.get("averageVolume")),
            volume_ratio=safe_float(info.get("volumeRatio")),
            market_cap=safe_float(info.get("marketCap")),
            enterprise_value=safe_float(info.get("enterpriseValue")),
            trailing_pe=safe_float(info.get("trailingPE")),
            forward_pe=safe_float(info.get("forwardPE")),
            peg_ratio=safe_float(info.get("pegRatio")),
            price_to_book=safe_float(info.get("priceToBook")),
            price_to_sales=safe_float(info.get("priceToSalesTrailing12Months")),
            gross_margin=safe_float(info.get("grossMargins")),
            operating_margin=safe_float(info.get("operatingMargins")),
            profit_margin=safe_float(info.get("profitMargins")),
            return_on_equity=safe_float(info.get("returnOnEquity")),
            return_on_assets=safe_float(info.get("returnOnAssets")),
            revenue_growth=safe_float(info.get("revenueGrowth")),
            earnings_growth=safe_float(info.get("earningsGrowth")),
            revenue=safe_float(info.get("totalRevenue")),
            revenue_per_share=safe_float(info.get("revenuePerShare")),
            dividend_rate=safe_float(info.get("dividendRate")),
            dividend_yield=safe_float(info.get("dividendYield")),
            ex_dividend_date=str(info.get("exDividendDate"))
            if info.get("exDividendDate")
            else None,
            payout_ratio=safe_float(info.get("payoutRatio")),
            total_debt=safe_float(info.get("totalDebt")),
            debt_to_equity=safe_float(info.get("debtToEquity")),
            current_ratio=safe_float(info.get("currentRatio")),
            quick_ratio=safe_float(info.get("quickRatio")),
            recommendation=info.get("recommendationKey"),
            target_mean_price=safe_float(info.get("targetMeanPrice")),
            target_high_price=safe_float(info.get("targetHighPrice")),
            target_low_price=safe_float(info.get("targetLowPrice")),
            num_analysts=safe_int(info.get("numberOfAnalystOpinions")),
        )

    except Exception as e:
        return StockFinancialsResponse(
            success=False,
            ticker=ticker.upper(),
            error=f"Error fetching financial data for {ticker}: {str(e)}",
        )


def get_stock_price_history_core(ticker: str, period: str = "1y") -> StockPriceHistoryResponse:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return StockPriceHistoryResponse(
                success=False,
                ticker=ticker.upper(),
                period=period,
                error=f"No historical data available for {ticker}",
            )

        recent_prices = []
        for idx, row in hist.tail(10).iterrows():
            date_str = str(idx)[:10]
            recent_prices.append(
                PriceHistoryDataPoint(
                    date=date_str,
                    open=round(float(row.iloc[0]), 2),
                    high=round(float(row.iloc[1]), 2),
                    low=round(float(row.iloc[2]), 2),
                    close=round(float(row.iloc[3]), 2),
                    volume=int(float(row.iloc[4])),
                )
            )

        close_series = hist["Close"]
        volume_series = hist["Volume"]

        return StockPriceHistoryResponse(
            success=True,
            ticker=ticker.upper(),
            period=period,
            start_date=str(hist.index[0])[:10],
            end_date=str(hist.index[-1])[:10],
            data_points=len(hist),
            avg_close=round(float(close_series.mean()), 2),
            min_close=round(float(close_series.min()), 2),
            max_close=round(float(close_series.max()), 2),
            total_volume=int(float(volume_series.sum())),
            avg_volume=int(float(volume_series.mean())),
            recent_prices=recent_prices,
        )

    except Exception as e:
        return StockPriceHistoryResponse(
            success=False,
            ticker=ticker.upper(),
            period=period,
            error=f"Error fetching price history for {ticker}: {str(e)}",
        )


@tool("Stock Financial Data")
def get_stock_financials(ticker: str) -> StockFinancialsResponse:
    """Get stock financial data."""
    return get_stock_financials_core(ticker)


@tool("Stock Price History")
def get_stock_price_history(ticker: str, period: str = "1y") -> StockPriceHistoryResponse:
    """Get stock price history."""
    return get_stock_price_history_core(ticker, period)
