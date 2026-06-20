from typing import List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., description="Role of the chat message sender")
    content: str = Field(..., description="Message content")


class ChatQueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Medical question from user",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional client session id",
    )


class ChatCompletionResponse(BaseModel):
    session_id: str
    answer: str
    messages: List[Message]


class LiveResponse(BaseModel):
    status: str
    pid: int
    uptime_seconds: float


class ReadyResponse(BaseModel):
    status: str
    ready: bool
    vectorstore_initialized: bool
    graph_initialized: bool
    init_error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    liveness: LiveResponse
    readiness: ReadyResponse
    timestamp_utc: str


class AppMetricsResponse(BaseModel):
    queries_total: int
    queries_failed: int
    last_query_time_utc: Optional[str]
    last_error: Optional[str]
