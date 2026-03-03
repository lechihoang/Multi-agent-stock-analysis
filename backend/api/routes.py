from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict, Any
import uuid
import logging

from backend.models.schemas import (
    ResearchRequest,
    JobStatusResponse,
    ResearchResponse,
    JobStatus,
)
from backend.middleware.rate_limiter import rate_limiter
from backend.orchestrator.orchestrator import MCPOrchestrator
from backend.orchestrator.query_analyzer import QueryAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["research"])

jobs: Dict[str, Dict[str, Any]] = {}

orchestrator = MCPOrchestrator()


def run_research_task(job_id: str, query: str):
    try:
        jobs[job_id]["status"] = JobStatus.PROCESSING

        result = orchestrator.execute_sync(query)

        if result.success:
            jobs[job_id]["status"] = JobStatus.COMPLETED
            jobs[job_id]["ticker"] = result.ticker
            jobs[job_id]["report"] = result.final_report
            jobs[job_id]["execution_time"] = result.total_execution_time
        else:
            jobs[job_id]["status"] = JobStatus.FAILED
            jobs[job_id]["error"] = result.error

    except Exception as e:
        logger.error(f"Research task failed: {str(e)}")
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)


@router.post("/research", response_model=JobStatusResponse)
async def create_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    if not rate_limiter.is_allowed():
        remaining = rate_limiter.get_remaining()
        reset_time = rate_limiter.get_reset_time()
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Rate limit exceeded",
                "remaining": remaining,
                "reset_in_seconds": int(reset_time),
            },
        )

    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "query": request.query,
        "ticker": "",
        "status": JobStatus.PENDING,
        "report": None,
        "execution_time": None,
        "error": None,
    }

    background_tasks.add_task(run_research_task, job_id, request.query)

    return JobStatusResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        query=request.query,
    )


@router.get("/research/{job_id}", response_model=ResearchResponse)
async def get_research(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    return ResearchResponse(
        job_id=job["job_id"],
        query=job["query"],
        ticker=job.get("ticker", ""),
        status=job["status"],
        report=job.get("report"),
        execution_time=job.get("execution_time"),
        error=job.get("error"),
    )


@router.post("/analyze")
async def analyze_query(request: ResearchRequest):
    try:
        analyzer = QueryAnalyzer()
        intent = analyzer.analyze(request.query)

        return {
            "original_query": intent.original_query,
            "ticker": intent.ticker,
            "agents_needed": intent.agents_needed,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "jobs_count": len(jobs),
    }


@router.get("/rate-limit")
async def get_rate_limit():
    return {
        "max_per_minute": rate_limiter.max_per_minute,
        "remaining": rate_limiter.get_remaining(),
        "reset_in_seconds": int(rate_limiter.get_reset_time()),
    }
