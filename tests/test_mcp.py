import os
import sys
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
class TestMCPToolSchemas:
    def test_mcp_tools_exist(self):
        from backend.mcp_server import (
            research_stock,
            get_stock_price,
            get_financial_metrics,
            search_financial_news,
            analyze_sentiment,
            analyze_risk,
            get_price_history,
            parse_stock_query,
        )
        required_tools = [
            research_stock,
            get_stock_price,
            get_financial_metrics,
            search_financial_news,
            analyze_sentiment,
            analyze_risk,
            get_price_history,
            parse_stock_query,
        ]
        for tool in required_tools:
            assert callable(tool), f"Tool {tool} is not callable"
            assert tool.__doc__ is not None, f"Tool {tool} missing docstring"
class TestMCPServerTools:
    def test_get_stock_price(self):
        from backend.mcp_server import get_stock_price
        result = get_stock_price("AAPL")
        assert result["success"] is True
        assert result["ticker"] == "AAPL"
        assert "current_price" in result
        assert "timestamp" in result
    def test_get_stock_price_invalid_ticker(self):
        from backend.mcp_server import get_stock_price
        result = get_stock_price("INVALID_TICKER_XYZ123")
        assert "ticker" in result
        assert "timestamp" in result
    def test_get_financial_metrics(self):
        from backend.mcp_server import get_financial_metrics
        result = get_financial_metrics("MSFT")
        assert result["success"] is True
        assert result["ticker"] == "MSFT"
        assert "pe_ratio" in result
        assert "market_cap" in result or result.get("error") is None
    def test_search_financial_news(self):
        from backend.mcp_server import search_financial_news
        result = search_financial_news("NVDA stock news", max_results=5)
        assert result["success"] is True
        assert result["query"] == "NVDA stock news"
        assert "results" in result
    def test_get_price_history(self):
        from backend.mcp_server import get_price_history
        result = get_price_history("GOOGL", period="1mo")
        assert result["success"] is True
        assert result["ticker"] == "GOOGL"
        assert "recent_prices" in result
        assert "statistics" in result
    def test_parse_stock_query(self):
        from backend.mcp_server import parse_stock_query
        result = parse_stock_query("How is Apple stock doing today?")
        assert "original_query" in result
        assert "timestamp" in result
        if result["success"]:
            assert "ticker" in result
            assert "query_type" in result
            assert "agents_needed" in result
class TestMCPResources:
    def test_company_profile_resource(self):
        from backend.mcp_server import get_company_profile
        result = get_company_profile("AAPL")
        assert "Company Profile" in result or "AAPL" in result
        assert isinstance(result, str)
    def test_stock_summary_resource(self):
        from backend.mcp_server import get_stock_summary
        result = get_stock_summary("TSLA")
        assert "TSLA" in result
        assert isinstance(result, str)
@pytest.mark.integration
class TestMCPIntegration:
    @pytest.fixture(autouse=True)
    def check_api_keys(self):
        if not os.getenv("NVIDIA_API_KEY"):
            pytest.skip("NVIDIA_API_KEY not set")
        if not os.getenv("TAVILY_API_KEY"):
            pytest.skip("TAVILY_API_KEY not set")
    @pytest.mark.asyncio
    async def test_full_research_workflow(self):
        from backend.mcp_server import research_stock
        result = await research_stock("How is AAPL doing?")
        assert result["success"] is True
        assert result["ticker"] == "AAPL"
        assert "report" in result
        assert "execution_time_seconds" in result
    def test_sentiment_analysis_tool(self):
        from backend.mcp_server import analyze_sentiment
        result = analyze_sentiment("TSLA")
        assert result["success"] is True
        assert result["ticker"] == "TSLA"
    def test_risk_analysis_tool(self):
        from backend.mcp_server import analyze_risk
        result = analyze_risk("NVDA")
        assert result["success"] is True
        assert result["ticker"] == "NVDA"
class TestMCPProtocolCompliance:
    def test_tool_response_format(self):
        from backend.mcp_server import get_stock_price
        result = get_stock_price("AAPL")
        assert isinstance(result, dict)
        assert "success" in result
        assert "timestamp" in result
    def test_error_response_format(self):
        from backend.mcp_server import get_stock_price
        result = get_stock_price("")
        assert isinstance(result, dict)
        assert "timestamp" in result
    def test_tool_has_docstring(self):
        from backend.mcp_server import (
            research_stock,
            get_stock_price,
            get_financial_metrics,
            search_financial_news,
            analyze_sentiment,
            analyze_risk,
            get_price_history,
            parse_stock_query,
        )
        tools = [
            research_stock,
            get_stock_price,
            get_financial_metrics,
            search_financial_news,
            analyze_sentiment,
            analyze_risk,
            get_price_history,
            parse_stock_query,
        ]
        for tool in tools:
            assert tool.__doc__ is not None, f"Missing docstring for {tool.__name__}"
            assert len(tool.__doc__) > 50, f"Docstring too short for {tool.__name__}"
class TestMCPPerformance:
    def test_stock_price_response_time(self):
        import time
        from backend.mcp_server import get_stock_price
        start = time.time()
        result = get_stock_price("AAPL")
        elapsed = time.time() - start
        assert elapsed < 5.0, f"Tool took too long: {elapsed:.2f}s"
        assert result["success"] is True
    def test_financial_metrics_response_time(self):
        import time
        from backend.mcp_server import get_financial_metrics
        start = time.time()
        result = get_financial_metrics("MSFT")
        elapsed = time.time() - start
        assert elapsed < 5.0, f"Tool took too long: {elapsed:.2f}s"
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])