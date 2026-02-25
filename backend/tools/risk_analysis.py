from crewai.tools import tool
import yfinance as yf

from backend.models.outputs import RiskMetricsResponse


def calculate_risk_metrics_core(ticker: str) -> RiskMetricsResponse:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        beta = info.get("beta")
        if beta is None:
            beta = 1.0

        beta_3_year = info.get("beta_3_year")
        if beta_3_year is not None:
            beta_3_year = round(beta_3_year, 2)

        debt_to_equity = info.get("debtToEquity")
        if debt_to_equity is not None:
            debt_to_equity = round(debt_to_equity, 2)

        current_ratio = info.get("currentRatio")
        if current_ratio is not None:
            current_ratio = round(current_ratio, 2)

        return RiskMetricsResponse(
            success=True,
            ticker=ticker.upper(),
            beta=round(beta, 2),
            beta_3_year=beta_3_year,
            debt_to_equity=debt_to_equity,
            current_ratio=current_ratio,
        )

    except Exception as e:
        return RiskMetricsResponse(
            success=False,
            ticker=ticker.upper(),
            error=f"Error calculating risk metrics for {ticker}: {str(e)}",
        )


@tool("Calculate Risk Metrics")
def calculate_risk_metrics(ticker: str) -> RiskMetricsResponse:
    """Calculate risk metrics for a stock."""
    return calculate_risk_metrics_core(ticker)
