# MCP Architecture - Stock Research Agent

## Overview

This document describes the Model Context Protocol (MCP) implementation for the Stock Research Agent, enabling standardized AI-tool communication via JSON-RPC 2.0 protocol.

## Architecture Diagram

```
                           MCP PROTOCOL LAYER
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │   ┌─────────────────┐         ┌─────────────────────────┐  │
    │   │   MCP Clients   │         │   External MCP Servers  │  │
    │   │                 │         │                         │  │
    │   │  - Cursor IDE   │◄───────►│  - GitHub MCP           │  │
    │   │  - Claude       │ JSON-RPC│  - PostgreSQL MCP       │  │
    │   │  - Custom Apps  │         │  - Filesystem MCP       │  │
    │   └────────┬────────┘         └─────────────────────────┘  │
    │            │                              ▲                 │
    │            │ stdio/SSE                    │                 │
    │            ▼                              │                 │
    │   ┌────────────────────────────────────────────────────┐   │
    │   │           STOCK RESEARCH MCP SERVER                │   │
    │   │                                                    │   │
    │   │   ┌──────────────────────────────────────────┐    │   │
    │   │   │            MCP TOOLS                      │    │   │
    │   │   │  ┌─────────────────┐ ┌────────────────┐  │    │   │
    │   │   │  │ research_stock  │ │ get_stock_price│  │    │   │
    │   │   │  └─────────────────┘ └────────────────┘  │    │   │
    │   │   │  ┌─────────────────┐ ┌────────────────┐  │    │   │
    │   │   │  │get_financial_   │ │search_financial│  │    │   │
    │   │   │  │    metrics      │ │     _news      │  │    │   │
    │   │   │  └─────────────────┘ └────────────────┘  │    │   │
│   │   │  ┌─────────────────┐ ┌────────────────┐  │    │   │
│   │   │  │analyze_sentiment│ │  analyze_risk  │  │    │   │
│   │   │  └─────────────────┘ └────────────────┘  │    │   │
│   │   │  ┌─────────────────┐ ┌────────────────┐  │    │   │
│   │   │  │get_price_       │ │parse_stock_    │  │    │   │
│   │   │  │   history       │ │    query       │  │    │   │
│   │   │  └─────────────────┘ └────────────────┘  │    │   │
│   │   │  ┌─────────────────┐ ┌────────────────┐  │    │   │
│   │   │  │extract_company  │ │ lookup_ticker  │  │    │   │
│   │   │  └─────────────────┘ └────────────────┘  │    │   │
    │   │   └──────────────────────────────────────────┘    │   │
    │   │                        │                           │   │
    │   │   ┌────────────────────┴────────────────────┐     │   │
    │   │   │           MCP RESOURCES                 │     │   │
    │   │   │  stock://{ticker}/profile               │     │   │
    │   │   │  stock://{ticker}/summary               │     │   │
    │   │   └─────────────────────────────────────────┘     │   │
    │   │                        │                           │   │
    │   │   ┌────────────────────┴────────────────────┐     │   │
    │   │   │           MCP PROMPTS                   │     │   │
    │   │   │  stock_research_prompt                  │     │   │
    │   │   │  quick_price_check_prompt               │     │   │
    │   │   │  risk_analysis_prompt                   │     │   │
    │   │   └─────────────────────────────────────────┘     │   │
    │   └────────────────────────────────────────────────────┘   │
    │                            │                               │
    └────────────────────────────┼───────────────────────────────┘
                                 │
                                 ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    CREWAI ORCHESTRATOR                      │
    │                                                             │
    │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
    │   │  Price   │ │Financial │ │   News   │ │  Market  │      │
    │   │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │      │
    │   └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│   ┌──────────┐ ┌──────────┐                                │
│   │Sentiment │ │   Risk   │                                │
│   │  Agent   │ │  Agent   │                                │
│   └──────────┘ └──────────┘                                │
    │                        │                                    │
    │                        ▼                                    │
    │               ┌──────────────┐                             │
    │               │  Synthesis   │                             │
    │               │    Agent     │                             │
    │               └──────────────┘                             │
    │                        │                                    │
    │                        ▼                                    │
    │               ┌──────────────┐                             │
    │               │   Research   │                             │
    │               │    Report    │                             │
    │               └──────────────┘                             │
    └─────────────────────────────────────────────────────────────┘
```

## MCP Components

### 1. MCP Tools

Tools are callable functions exposed via JSON-RPC protocol:

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `research_stock` | Full multi-agent research workflow | `query: str` | Structured research report |
| `get_stock_price` | Real-time stock price data | `ticker: str` | Price data with change% |
| `get_financial_metrics` | Financial fundamentals | `ticker: str` | P/E, margins, growth metrics |
| `search_financial_news` | Search financial news | `query: str, max_results: int` | News articles list |
| `analyze_sentiment` | Social media sentiment | `ticker: str` | Sentiment scores |
| `analyze_risk` | Quantitative risk metrics | `ticker: str` | VaR, Beta, Volatility |
| `get_price_history` | Historical OHLCV data | `ticker: str, period: str` | Price history |
| `parse_stock_query` | NLP query parsing | `query: str` | Ticker, intent, agents |
| `extract_company` | Extract company name from query | `query: str` | Company name |
| `lookup_ticker` | Lookup ticker symbol | `query: str` | Ticker symbol |

### 2. MCP Resources

Static data endpoints accessible via URI scheme:

```
stock://{ticker}/profile  - Company profile and description
stock://{ticker}/summary  - Quick stock summary
```

### 3. MCP Prompts

Pre-defined prompt templates:

- `stock_research_prompt(ticker)` - Comprehensive research template
- `quick_price_check_prompt(ticker)` - Quick price check template
- `risk_analysis_prompt(ticker)` - Risk-focused analysis template

## Protocol Specification

### JSON-RPC 2.0 Communication

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_stock_price",
    "arguments": {
      "ticker": "AAPL"
    }
  }
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"ticker\": \"AAPL\", \"current_price\": 264.72, ...}"
      }
    ]
  }
}
```

### Transport Protocols

- **stdio**: Standard input/output (local execution)
- **SSE**: Server-Sent Events (remote execution)

## File Structure

```
stock-research-agent/
├── backend/
│   ├── mcp_server.py              # Main MCP server (FastMCP)
│   ├── main.py                    # FastAPI app
│   ├── api/
│   │   └── routes.py              # REST API endpoints
│   ├── config/
│   │   └── settings.py            # Configuration
│   ├── middleware/
│   │   └── rate_limiter.py        # Rate limiting
│   ├── orchestrator/
│   │   ├── mcp_orchestrator.py    # CrewAI orchestration
│   │   └── query_analyzer.py      # Query parsing
│   ├── crew/
│   │   └── llm_config.py          # LLM config
│   ├── tools/
│   │   ├── stock_data.py          # yfinance integration
│   │   ├── tavily_search.py       # Tavily search
│   │   ├── sentiment_analysis.py  # Sentiment analysis
│   │   ├── risk_analysis.py       # Risk metrics
│   │   ├── entity_extraction.py   # Company extraction
│   │   ├── ticker_lookup.py       # Ticker lookup
│   │   └── utils.py               # Utilities
│   └── models/
│       ├── outputs.py              # Pydantic outputs
│       └── schemas.py              # API schemas
├── frontend/                      # React frontend
├── mcp.json                       # MCP server config
└── docs/
    └── MCP_ARCHITECTURE.md        # This document
```

## Usage

### Running the MCP Server

```bash
# Direct execution
python -m backend.mcp_server

# Via MCP CLI
mcp run backend/mcp_server.py

# With environment variables
NVIDIA_API_KEY=xxx TAVILY_API_KEY=xxx python -m backend.mcp_server
```

### Configuration (mcp.json)

```json
{
  "mcpServers": {
    "stock-research": {
      "command": "python",
      "args": ["-m", "backend.mcp_server"],
      "env": {
        "NVIDIA_API_KEY": "${NVIDIA_API_KEY}",
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      }
    }
  }
}
```

### Programmatic Usage

```python
from backend.mcp_server import get_stock_price, research_stock
import asyncio

# Sync tool call
result = get_stock_price("AAPL")
print(result["current_price"])

# Async research workflow
async def main():
    result = await research_stock("How is Tesla doing?")
    print(result["report"]["executive_summary"])

asyncio.run(main())
```

## Integration with CrewAI

The MCP server wraps CrewAI's multi-agent workflow:

1. **Query Analysis**: Parse natural language → extract ticker, intent
2. **Agent Selection**: Determine which agents to run based on query type
3. **Parallel Execution**: Run 6 specialized agents concurrently
4. **Context Aggregation**: Merge structured outputs from all agents
5. **Report Synthesis**: Generate comprehensive research report

### Agent Mapping

| Agent | MCP Tool | Pydantic Output |
|-------|----------|-----------------|
| Price Agent | `get_stock_price` | `PriceData` |
| Financial Agent | `get_financial_metrics` | `FinancialMetrics` |
| News Agent | `search_financial_news` | `NewsAnalysis` |
| Market Agent | `get_price_history` | `MarketTrends` |
| Sentiment Agent | `analyze_sentiment` | `SentimentData` |
| Risk Agent | `analyze_risk` | `RiskAssessment` |
| Query Parser | `parse_stock_query` | QueryIntent |
| Entity Extractor | `extract_company` | str |
| Ticker Lookup | `lookup_ticker` | str |

## Security Considerations

1. **API Key Management**: Store keys in environment variables, not in code
2. **Input Validation**: All tool inputs validated via Pydantic schemas
3. **Error Handling**: Graceful error responses with proper error codes
4. **Rate Limiting**: External API calls respect rate limits
5. **Logging**: Comprehensive logging for audit trails

## Performance

| Metric | Value |
|--------|-------|
| Single tool latency | < 3 seconds |
| Full research workflow | 20-50 seconds |
| Parallel agent execution | 6 agents concurrent |
| API calls per research | ~15-20 calls |
| MCP Tools available | 10 tools |
| MCP Resources | 2 resources |
| MCP Prompts | 3 prompts |

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [CrewAI Documentation](https://docs.crewai.com/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
