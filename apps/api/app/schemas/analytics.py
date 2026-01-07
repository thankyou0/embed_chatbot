"""Analytics schemas"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class AnalyticsOverviewResponse(BaseModel):
    total_sessions: int
    total_messages: int
    avg_messages_per_session: float
    deflection_rate: float  # % of sessions where all queries were answered
    unanswered_rate: float  # % of user queries that weren't answered confidently
    period: str  # "7d", "30d", "90d"


class UnansweredQuerySample(BaseModel):
    id: UUID
    content: str
    created_at: datetime


class UnansweredQuery(BaseModel):
    query: str
    count: int
    avg_confidence: float
    first_asked: datetime
    last_asked: datetime
    sample_messages: List[UnansweredQuerySample]


class UnansweredQueriesResponse(BaseModel):
    queries: List[UnansweredQuery]
    total_unanswered: int

