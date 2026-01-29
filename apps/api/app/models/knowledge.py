import enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Float, Enum as SAEnum, func, TypeDecorator, Boolean
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class KnowledgeSourceType(str, enum.Enum):
    CRAWLED_URL = "crawled_url"
    UPLOADED_FILE = "uploaded_file"
    QA_PAIR = "qa_pair"


class KnowledgeSourceStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CRAWLING = "crawling"
    COMPLETED = "completed"
    FAILED = "failed"


class ScheduleType(str, enum.Enum):
    MANUAL = "manual"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class CrawlStatus(str, enum.Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class KnowledgeSourceTypeDB(TypeDecorator):
    """Custom type for KnowledgeSourceType enum"""
    impl = PG_ENUM
    cache_ok = True
    
    def __init__(self):
        super().__init__("crawled_url", "uploaded_file", "qa_pair", name="knowledgesourcetype", create_type=False)
    
    def process_bind_param(self, value, dialect):
        if value is None: return None
        if isinstance(value, KnowledgeSourceType): return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None: return None
        return KnowledgeSourceType(value)


class KnowledgeSourceStatusDB(TypeDecorator):
    """Custom type for KnowledgeSourceStatus enum"""
    impl = PG_ENUM
    cache_ok = True
    
    def __init__(self):
        super().__init__("pending", "processing", "crawling", "completed", "failed", name="knowledgesourcestatus", create_type=False)
    
    def process_bind_param(self, value, dialect):
        if value is None: return None
        if isinstance(value, KnowledgeSourceStatus): return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None: return None
        return KnowledgeSourceStatus(value)


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    chatbot_id = Column(ForeignKey("chatbots.id"), nullable=False, index=True)
    source_type = Column(KnowledgeSourceTypeDB(), nullable=False)
    source_url = Column(String(2048), nullable=True)
    status = Column(KnowledgeSourceStatusDB(), nullable=False, default=KnowledgeSourceStatus.PENDING)
    pages_found = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)  # Store error message when status is FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    chatbot = relationship("Chatbot", back_populates="knowledge_sources")
    pages = relationship("CrawledPage", back_populates="knowledge_source", cascade="all, delete-orphan")
    files = relationship("UploadedFile", back_populates="knowledge_source", cascade="all, delete-orphan")
    qa_pairs = relationship("QAPair", back_populates="knowledge_source", cascade="all, delete-orphan", order_by="asc(QAPair.created_at), asc(QAPair.id)")
    crawl_history = relationship("CrawlHistory", back_populates="knowledge_source", cascade="all, delete-orphan")
    crawl_schedule = relationship("CrawlSchedule", back_populates="knowledge_source", cascade="all, delete-orphan", uselist=False)


class CrawledPage(Base):
    __tablename__ = "crawled_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    knowledge_source_id = Column(ForeignKey("knowledge_sources.id"), nullable=False, index=True)
    url = Column(String(2048), nullable=False)
    title = Column(String(1024), nullable=True)
    content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)
    is_removed = Column(Boolean, nullable=False, default=False)
    is_product = Column(Boolean, nullable=False, default=False)  # Quick filter for product pages
    product_metadata = Column(JSONB, nullable=True)  # Structured product data (price, images, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    knowledge_source = relationship("KnowledgeSource", back_populates="pages")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    knowledge_source_id = Column(ForeignKey("knowledge_sources.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    content_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    knowledge_source = relationship("KnowledgeSource", back_populates="files")


class QAPair(Base):
    __tablename__ = "qa_pairs"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    knowledge_source_id = Column(ForeignKey("knowledge_sources.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    knowledge_source = relationship("KnowledgeSource", back_populates="qa_pairs")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    chatbot_id = Column(ForeignKey("chatbots.id"), nullable=False, index=True)
    knowledge_source_id = Column(ForeignKey("knowledge_sources.id"), nullable=False, index=True)
    source_type = Column(KnowledgeSourceTypeDB(), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)  # 384 for all-MiniLM-L6-v2
    metadata_json = Column(JSONB, nullable=False, server_default='{}')
    priority_weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    chatbot = relationship("Chatbot")
    knowledge_source = relationship("KnowledgeSource")


class ScheduleTypeDB(TypeDecorator):
    """Custom type for ScheduleType enum"""
    impl = PG_ENUM
    cache_ok = True
    
    def __init__(self):
        super().__init__("manual", "daily", "weekly", "monthly", name="scheduletype", create_type=False)
    
    def process_bind_param(self, value, dialect):
        if value is None: return None
        if isinstance(value, ScheduleType): return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None: return None
        return ScheduleType(value)


class CrawlStatusDB(TypeDecorator):
    """Custom type for CrawlStatus enum"""
    impl = PG_ENUM
    cache_ok = True
    
    def __init__(self):
        super().__init__("success", "partial", "failed", name="crawlstatus", create_type=False)
    
    def process_bind_param(self, value, dialect):
        if value is None: return None
        if isinstance(value, CrawlStatus): return value.value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None: return None
        return CrawlStatus(value)


class CrawlSchedule(Base):
    __tablename__ = "crawl_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    knowledge_source_id = Column(ForeignKey("knowledge_sources.id"), nullable=False, index=True, unique=True)
    schedule_type = Column(ScheduleTypeDB(), nullable=False, default=ScheduleType.MANUAL)
    day_of_week = Column(Integer, nullable=True)  # 0-6 for weekly (0=Monday)
    preferred_hour = Column(Integer, nullable=False, default=2)  # 0-23, UTC
    is_active = Column(Boolean, nullable=False, default=True)
    last_crawl_at = Column(DateTime(timezone=True), nullable=True)
    next_crawl_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    knowledge_source = relationship("KnowledgeSource", back_populates="crawl_schedule")


class CrawlHistory(Base):
    __tablename__ = "crawl_history"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    knowledge_source_id = Column(ForeignKey("knowledge_sources.id"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(CrawlStatusDB(), nullable=False)
    pages_checked = Column(Integer, nullable=False, default=0)
    pages_added = Column(Integer, nullable=False, default=0)
    pages_updated = Column(Integer, nullable=False, default=0)
    pages_removed = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)

    # Relationships
    knowledge_source = relationship("KnowledgeSource", back_populates="crawl_history")

