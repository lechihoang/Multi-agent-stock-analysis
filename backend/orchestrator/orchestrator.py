import asyncio
import logging
import warnings
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from crewai import Agent, Task, Crew
from backend.orchestrator.query_analyzer import QueryAnalyzer, QueryIntent
from backend.crew.llm_config import get_llm
from backend.tools.tavily_search import tavily_search
from backend.tools.stock_data import get_stock_price, get_stock_financials, get_stock_price_history
from backend.tools.sentiment_analysis import analyze_stock_sentiment, get_social_mentions
from backend.tools.risk_analysis import calculate_risk_metrics
from backend.models.outputs import (
    PriceData,
    FinancialMetrics,
    NewsAnalysis,
    MarketTrends,
    SentimentData,
    RiskAssessment,
    ResearchReport,
    AgentOutput,
)

logging.getLogger("crewai").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*CrewAIEventsBus.*")
logger = logging.getLogger(__name__)


class StructuredOutputError(Exception):
    pass


@dataclass
class AgentResult:
    agent_name: str
    success: bool
    output: str
    structured_output: AgentOutput
    execution_time: float = 0.0
    error: Optional[str] = None


@dataclass
class OrchestratorResult:
    success: bool
    ticker: str
    agent_results: List[AgentResult]
    structured_report: Optional[ResearchReport] = None
    final_report: str = ""
    total_execution_time: float = 0.0
    error: Optional[str] = None


class MCPOrchestrator:
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.llm = get_llm()

    def create_price_agent(self) -> Agent:
        return Agent(
            role="Stock Price Analyst",
            goal="Get real-time stock price and trading data",
            backstory="You are an expert at analyzing stock prices and trading data. You excel at extracting current price information, volume data, and market statistics.",
            tools=[get_stock_price, get_stock_price_history],
            llm=self.llm,
        )

    def create_financial_agent(self) -> Agent:
        return Agent(
            role="Financial Analyst",
            goal="Analyze financial metrics and company fundamentals",
            backstory="You are a financial analyst with deep expertise in reading financial statements, analyzing ratios, and evaluating company fundamentals.",
            tools=[get_stock_financials],
            llm=self.llm,
        )

    def create_news_agent(self) -> Agent:
        return Agent(
            role="News Analyst",
            goal="Find and analyze latest news and developments",
            backstory="You are a news analyst specialized in finding and summarizing the latest developments affecting stocks and companies.",
            tools=[tavily_search],
            llm=self.llm,
        )

    def create_market_agent(self) -> Agent:
        return Agent(
            role="Market Trend Analyst",
            goal="Analyze market position, trends, and technical indicators",
            backstory="You are a market trend analyst with expertise in technical analysis, chart patterns, and identifying market trends.",
            tools=[get_stock_price_history, tavily_search],
            llm=self.llm,
        )

    def create_sentiment_agent(self) -> Agent:
        return Agent(
            role="Sentiment Analyst",
            goal="Analyze market sentiment from social media and news sources",
            backstory="You are a sentiment analyst who specializes in gauging market mood through social media trends, news tone, and investor sentiment indicators.",
            tools=[analyze_stock_sentiment, get_social_mentions, tavily_search],
            llm=self.llm,
        )

    def create_risk_agent(self) -> Agent:
        return Agent(
            role="Risk Analyst",
            goal="Quantify and assess investment risks using statistical metrics",
            backstory="You are a risk analyst with deep expertise in statistical risk metrics, VaR calculations, and portfolio risk assessment.",
            tools=[calculate_risk_metrics, get_stock_price_history],
            llm=self.llm,
        )

    def create_synthesis_agent(self) -> Agent:
        return Agent(
            role="Investment Report Editor",
            goal="Compile research findings into a comprehensive report",
            backstory="You are an investment report editor who excels at synthesizing complex financial analysis into clear, actionable research reports.",
            tools=[],
            llm=self.llm,
        )

    def get_agent_factory(self, agent_type: str):
        factories = {
            "price": self.create_price_agent,
            "financial": self.create_financial_agent,
            "news": self.create_news_agent,
            "market": self.create_market_agent,
            "sentiment": self.create_sentiment_agent,
            "risk": self.create_risk_agent,
        }
        return factories.get(agent_type)

    def get_output_model(self, agent_type: str) -> type:
        models = {
            "price": PriceData,
            "financial": FinancialMetrics,
            "news": NewsAnalysis,
            "market": MarketTrends,
            "sentiment": SentimentData,
            "risk": RiskAssessment,
            "synthesis": ResearchReport,
        }
        return models.get(agent_type, PriceData)

    def create_task_for_agent(self, agent: Agent, agent_type: str, ticker: str) -> Task:
        output_model = self.get_output_model(agent_type)
        task_configs = {
            "price": {
                "description": "Analyze current stock price and trading data",
                "expected_output": f"Comprehensive real-time price data for {ticker}",
            },
            "financial": {
                "description": "Analyze financial metrics and fundamentals",
                "expected_output": f"Detailed financial analysis for {ticker}",
            },
            "news": {
                "description": "Find and analyze latest news",
                "expected_output": f"Recent news summary for {ticker}",
            },
            "market": {
                "description": "Analyze market trends and technical indicators",
                "expected_output": f"Market trend analysis for {ticker}",
            },
            "sentiment": {
                "description": "Analyze market sentiment from various sources",
                "expected_output": f"Comprehensive sentiment analysis for {ticker}",
            },
            "risk": {
                "description": "Calculate and assess risk metrics",
                "expected_output": f"Quantitative risk assessment for {ticker}",
            },
        }
        config = task_configs.get(agent_type, {})
        return Task(
            description=config.get("description", f"Analyze {ticker}"),
            expected_output=config.get("expected_output", f"Analysis for {ticker}"),
            agent=agent,
            output_pydantic=output_model,
        )

    def extract_structured_output(self, crew_result, agent_type: str) -> AgentOutput:
        model_class = self.get_output_model(agent_type)
        if hasattr(crew_result, "pydantic") and crew_result.pydantic:
            if isinstance(crew_result.pydantic, model_class):
                return crew_result.pydantic
            try:
                return model_class.model_validate(crew_result.pydantic.model_dump())
            except Exception as e:
                raise StructuredOutputError(
                    f"Pydantic output type mismatch for {agent_type}: expected {model_class.__name__}, got {type(crew_result.pydantic).__name__}. Validation error: {e}"
                )
        if hasattr(crew_result, "tasks_output") and crew_result.tasks_output:
            for task_output in crew_result.tasks_output:
                if hasattr(task_output, "pydantic") and task_output.pydantic:
                    if isinstance(task_output.pydantic, model_class):
                        return task_output.pydantic
                    try:
                        return model_class.model_validate(task_output.pydantic.model_dump())
                    except Exception as e:
                        raise StructuredOutputError(
                            f"Task output type mismatch for {agent_type}: {e}"
                        )
        raw_output = ""
        if hasattr(crew_result, "raw"):
            raw_output = str(crew_result.raw)[:500]
        elif hasattr(crew_result, "output"):
            raw_output = str(crew_result.output)[:500]
        else:
            raw_output = str(crew_result)[:500]
        raise StructuredOutputError(
            f"Agent {agent_type} did not return structured output. Raw output: {raw_output}"
        )

    def run_single_agent(self, agent_type: str, ticker: str) -> AgentResult:
        start_time = datetime.now()
        try:
            agent_factory = self.get_agent_factory(agent_type)
            if not agent_factory:
                raise ValueError(f"Unknown agent type: {agent_type}")
            agent = agent_factory()
            task = self.create_task_for_agent(agent, agent_type, ticker)
            crew = Crew(
                agents=[agent],
                tasks=[task],
            )
            crew_result = crew.kickoff(inputs={"ticker": ticker})
            structured_output = self.extract_structured_output(crew_result, agent_type)
            raw_output = structured_output.model_dump_json(indent=2)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Agent {agent_type} completed in {execution_time:.2f}s")
            return AgentResult(
                agent_name=agent_type,
                success=True,
                output=raw_output,
                structured_output=structured_output,
                execution_time=execution_time,
            )
        except StructuredOutputError as e:
            raise
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"Agent {agent_type} failed: {error_msg}")
            raise StructuredOutputError(f"Agent {agent_type} failed: {error_msg}")

    async def run_agents_parallel(self, agent_types: List[str], ticker: str) -> List[AgentResult]:
        import concurrent.futures

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agent_types)) as executor:
            futures = [
                loop.run_in_executor(executor, self.run_single_agent, agent_type, ticker)
                for agent_type in agent_types
            ]
            results = await asyncio.gather(*futures, return_exceptions=True)
        agent_results = []
        errors = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"{agent_types[i]}: {str(result)}")
            else:
                agent_results.append(result)
        if errors:
            raise StructuredOutputError(f"Agent(s) failed: {'; '.join(errors)}")
        return agent_results

    def compile_structured_context(
        self, agent_results: List[AgentResult]
    ) -> Dict[str, AgentOutput]:
        mapping = {
            "price": "price_data",
            "financial": "financial_metrics",
            "news": "news_analysis",
            "market": "market_trends",
            "sentiment": "sentiment_data",
            "risk": "risk_assessment",
        }
        result = {}
        for r in agent_results:
            key = mapping.get(r.agent_name)
            if key:
                result[key] = r.structured_output
        return result

    def synthesize_report(
        self, ticker: str, agent_results: List[AgentResult]
    ) -> tuple[str, Optional[ResearchReport]]:
        context = self.compile_structured_context(agent_results)
        import json

        context_json = {}
        for key, value in context.items():
            context_json[key] = value.model_dump()
        context_str = json.dumps(context_json, indent=2)
        synthesis_agent = self.create_synthesis_agent()
        synthesis_task = Task(
            description=f"""Synthesize all research findings into a comprehensive investment report in markdown format.
            Include: Executive Summary, Key Metrics (current price, market cap, P/E ratio, dividend yield),
            Price Analysis, Financial Analysis, News Analysis, Market Analysis, Sentiment Analysis,
            Risk Analysis, Investment Outlook, Risk Factors, Opportunities, Recommendation (with rating, 
            price target, suitable for investor types, time horizon).

            Context from agents:
            {context_str}""",
            expected_output="A detailed investment research report in clean markdown format. Start directly with '# ' (the title). Do NOT include any intro phrases like 'I can give you a great answer' or 'Sure, here's'. Just output the markdown report.",
            agent=synthesis_agent,
            markdown=True,
        )
        crew = Crew(
            agents=[synthesis_agent],
            tasks=[synthesis_task],
        )
        crew_result = crew.kickoff(inputs={"ticker": ticker})
        text_report = str(crew_result)
        return text_report, None

    async def execute(self, query: str) -> OrchestratorResult:
        start_time = datetime.now()
        intent: Optional[QueryIntent] = None
        try:
            logger.info(f"Analyzing query: {query}")
            intent = self.query_analyzer.analyze(query)
            logger.info(f"Intent: ticker={intent.ticker}, agents={intent.agents_needed}")
            logger.info(f"Running {len(intent.agents_needed)} agents in parallel...")
            agent_results = await self.run_agents_parallel(intent.agents_needed, intent.ticker)
            logger.info("Synthesizing final report...")
            text_report, structured_report = self.synthesize_report(intent.ticker, agent_results)
            total_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Orchestration completed in {total_time:.2f}s")
            return OrchestratorResult(
                success=True,
                ticker=intent.ticker,
                agent_results=agent_results,
                structured_report=structured_report,
                final_report=text_report,
                total_execution_time=total_time,
            )
        except ValueError as e:
            total_time = (datetime.now() - start_time).total_seconds()
            raise ValueError(f"Query analysis failed: {e}")
        except StructuredOutputError as e:
            total_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Structured output error: {e}")
            raise
        except Exception as e:
            total_time = (datetime.now() - start_time).total_seconds()
            logger.exception(f"Unexpected error: {e}")
            raise StructuredOutputError(f"Unexpected error: {str(e)}")

    def execute_sync(self, query: str) -> OrchestratorResult:
        return asyncio.run(self.execute(query))
