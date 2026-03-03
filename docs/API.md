# API Documentation

## Endpoints

### POST /api/research

Create a new research job.

**Request:**
```json
{
  "query": "How is Apple stock doing?"
}
```

**Response:**
```json
{
  "job_id": "abc-123-def",
  "status": "pending",
  "query": "How is Apple stock doing?"
}
```

### GET /api/research/{job_id}

Get research job status and result.

**Response (completed):**
```json
{
  "job_id": "abc-123-def",
  "query": "How is Apple stock doing?",
  "ticker": "AAPL",
  "status": "completed",
  "report": "## Research Report\n\n...",
  "execution_time": 45.2
}
```

**Response (processing):**
```json
{
  "job_id": "abc-123-def",
  "query": "How is Apple stock doing?",
  "ticker": "AAPL",
  "status": "processing",
  "report": null,
  "execution_time": null
}
```

### POST /api/analyze

Parse query to extract ticker and agents.

**Request:**
```json
{
  "query": "How is Apple doing?"
}
```

**Response:**
```json
{
  "original_query": "How is Apple doing?",
  "ticker": "AAPL",
  "agents_needed": ["price", "financial", "news", "market", "sentiment", "risk"]
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "jobs_count": 5
}
```

### GET /api/rate-limit

Check current rate limit status.

**Response:**
```json
{
  "max_per_minute": 40,
  "remaining": 38,
  "reset_in_seconds": 45
}
```

## Status Codes

| Status | Description |
|--------|-------------|
| `pending` | Job created, waiting to start |
| `processing` | Agents are running |
| `completed` | Research finished |
| `failed` | Error occurred |
