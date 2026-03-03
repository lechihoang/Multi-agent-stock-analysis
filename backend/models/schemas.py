from pydantic import BaseModel, field_validator
from typing import Optional, List
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    """Request for stock research with natural language query."""

    query: str

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Query must be at least 3 characters")
        if len(v) > 500:
            raise ValueError("Query must be at most 500 characters")
        return v


class JobStatusResponse(BaseModel):
    """Response when creating a research job."""

    job_id: str
    status: JobStatus
    query: str


class ResearchResponse(BaseModel):
    """Response with research results."""

    job_id: str
    query: str
    ticker: str
    status: JobStatus
    report: Optional[str] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
