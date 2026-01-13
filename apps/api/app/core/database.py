from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Base class for models
Base = declarative_base()

# Global variables for engine and session
engine = None
AsyncSessionLocal = None


def get_engine():
    """Get or create the database engine"""
    global engine
    if engine is None:
        # Validate DATABASE_URL before creating engine
        if not settings.DATABASE_URL or settings.DATABASE_URL == "postgresql+asyncpg://postgres:post@localhost:5432/embed_chatbot":
            logger.warning("DATABASE_URL not set or using default value. Database operations may fail.")
        
        # Debug: Log URL structure (mask password)
        db_url = settings.DATABASE_URL.strip()  # Remove any whitespace
        try:
            # Mask password for logging
            if "@" in db_url:
                parts = db_url.split("@")
                if len(parts) == 2:
                    scheme_user_pass = parts[0]
                    host_db = parts[1]
                    if "://" in scheme_user_pass:
                        scheme = scheme_user_pass.split("://")[0]
                        user_pass = scheme_user_pass.split("://")[1]
                        if ":" in user_pass:
                            user = user_pass.split(":")[0]
                            masked_url = f"{scheme}://{user}:***@{host_db}"
                            logger.info(f"Database URL format: {masked_url}")
                            logger.debug(f"URL length: {len(db_url)}, starts with: {db_url[:20]}...")
        except Exception:
            pass
        
        # Try to create engine with better error handling
        try:
            engine = create_async_engine(
                db_url,
                echo=False,
                future=True,
            )
        except Exception as e:
            error_str = str(e)
            if "Could not parse" in error_str or "parse" in error_str.lower():
                logger.error("=" * 60)
                logger.error("DATABASE_URL PARSING ERROR")
                logger.error("=" * 60)
                logger.error(f"URL length: {len(db_url)} characters")
                logger.error(f"URL starts with: {repr(db_url[:50])}")
                logger.error(f"URL ends with: {repr(db_url[-50:])}")
                logger.error("Common issues:")
                logger.error("1. Special characters in password need URL encoding")
                logger.error("2. Hidden whitespace or newlines in the URL")
                logger.error("3. Password might be different from what you expect")
                logger.error("=" * 60)
                logger.error("Try URL-encoding the password using urllib.parse.quote_plus()")
                logger.error("Example: from urllib.parse import quote_plus; quote_plus('your_password')")
            raise
    return engine


def get_session_factory():
    """Get or create the async session factory"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return AsyncSessionLocal


async def check_database_connection() -> bool:
    """Test database connectivity and log the result."""
    try:
        eng = get_engine()
        async with eng.connect() as conn:
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
        session_factory = get_session_factory()
        async with session_factory() as session:
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

