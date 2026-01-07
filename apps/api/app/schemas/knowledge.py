from pydantic import BaseModel, HttpUrl, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models.knowledge import KnowledgeSourceType, KnowledgeSourceStatus, ScheduleType, CrawlStatus


class KnowledgeSourceBase(BaseModel):
    source_type: KnowledgeSourceType
    source_url: Optional[str] = None


class KnowledgeSourceCreate(BaseModel):
    base_url: str
    max_pages: Optional[int] = 500


class UploadedFileResponse(BaseModel):
    id: UUID
    knowledge_source_id: UUID
    filename: str
    file_size: int
    mime_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeSourceResponse(BaseModel):
    id: UUID
    chatbot_id: UUID
    source_type: KnowledgeSourceType
    source_url: Optional[str] = None
    status: KnowledgeSourceStatus
    pages_found: int
    created_at: datetime
    updated_at: datetime
    files: Optional[List[UploadedFileResponse]] = []
    qa_pairs: Optional[List['QAPairResponse']] = []
    pages: Optional[List['CrawledPageResponse']] = []

    class Config:
        from_attributes = True


class QAPairCreate(BaseModel):
    question: str
    answer: str


class QAPairBulkCreate(BaseModel):
    qa_pairs: List[QAPairCreate]


class QAPairResponse(BaseModel):
    id: UUID
    knowledge_source_id: UUID
    question: str
    answer: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    knowledge_source_id: UUID
    filename: str
    status: KnowledgeSourceStatus


class CrawledPageResponse(BaseModel):
    id: UUID
    knowledge_source_id: UUID
    url: str
    title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CrawlStatusResponse(BaseModel):
    id: UUID
    status: KnowledgeSourceStatus
    pages_found: int
    updated_at: datetime

    class Config:
        from_attributes = True


class BulkDeleteRequest(BaseModel):
    ids: List[UUID]


# ============== Crawl Scheduling Schemas ==============

class CrawlScheduleCreate(BaseModel):
    schedule_type: ScheduleType
    day_of_week: Optional[int] = None  # 0-6 for weekly (0=Monday)
    preferred_hour: int = 2  # 0-23, UTC
    is_active: bool = True


class CrawlScheduleUpdate(BaseModel):
    schedule_type: Optional[ScheduleType] = None
    day_of_week: Optional[int] = None
    preferred_hour: Optional[int] = None
    is_active: Optional[bool] = None


class CrawlScheduleResponse(BaseModel):
    id: UUID
    knowledge_source_id: UUID
    schedule_type: ScheduleType
    day_of_week: Optional[int] = None
    preferred_hour: int
    is_active: bool
    last_crawl_at: Optional[datetime] = None
    next_crawl_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CrawlHistoryResponse(BaseModel):
    id: UUID
    knowledge_source_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: CrawlStatus
    pages_checked: int
    pages_added: int
    pages_updated: int
    pages_removed: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class TriggerCrawlResponse(BaseModel):
    message: str
    crawl_history_id: UUID
