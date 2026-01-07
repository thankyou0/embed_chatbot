from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def check_database_connection() -> bool:
    """Test database connectivity and log the result."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            # Extract host info from DATABASE_URL for display
            db_host = settings.DATABASE_URL.split("@")[-1].split("/")[0] if "@" in settings.DATABASE_URL else "localhost"
            db_name = settings.DATABASE_URL.split("/")[-1].split("?")[0]
            logger.success(f"Database connected: {db_name}@{db_host}")
            return True
    except Exception as e:
        error_msg = str(e).lower()
        # Extract meaningful error message
        if "connection refused" in error_msg or "could not connect" in error_msg:
            logger.error("Database connection refused - is PostgreSQL running?")
        elif "password authentication failed" in error_msg or "authentication failed" in error_msg:
            logger.error("Database authentication failed - check credentials in .env")
        elif "does not exist" in error_msg or "database" in error_msg and "not found" in error_msg:
            db_name = settings.DATABASE_URL.split("/")[-1].split("?")[0]
            logger.error(f"Database '{db_name}' does not exist - create it in pgAdmin first")
        elif "relation" in error_msg and "does not exist" in error_msg:
            logger.warning("Database connected but tables missing - run migrations: alembic upgrade head")
            return True  # Connection works, just missing tables
        else:
            logger.error(f"Database connection failed: {str(e)[:80]}")
        return False


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except Exception as e:
                # logger.error(f"Database session error: {str(e)[:50]}")
                await session.rollback()
                raise
            finally:
                await session.close()
    except Exception as e:
        # Re-raise to be caught by database exception handler
        raise

