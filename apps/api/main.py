from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import traceback
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger, setup_uvicorn_logging
from app.core.exceptions import APIException, DatabaseError
from app.core.database import check_database_connection
from app.api.v1.router import api_router
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

# Initialize logger
logger = get_logger(__name__)

# Base path for the API directory
API_BASE_PATH = Path(__file__).parent

# Paths to exclude from source tracking (libraries, virtual environments)
EXCLUDED_SOURCE_PATTERNS = [
    ".venv", "venv", "site-packages", "dist-packages",
    "lib/python", "Lib\\site-packages", "\\Python", "/Python",
    "uvicorn", "starlette", "fastapi", "sqlalchemy", "pydantic",
    "anyio", "asyncpg", "logging", "asyncio",
]

# Infrastructure files to skip when finding error source
INFRASTRUCTURE_FILES = [
    "database.py",
    "dependencies.py",
    "exceptions.py",
    "logging.py",
    "main.py",
]


def _is_user_file(pathname: str) -> bool:
    """Check if the path is a user-created file (not from libraries)."""
    path_lower = pathname.lower()
    for pattern in EXCLUDED_SOURCE_PATTERNS:
        if pattern.lower() in path_lower:
            return False
    return True


def _is_infrastructure_file(pathname: str) -> bool:
    """Check if the file is infrastructure code (not the actual error source)."""
    filename = Path(pathname).name.lower()
    return filename in [f.lower() for f in INFRASTRUCTURE_FILES]


def get_user_source_from_traceback(tb) -> str:
    """Extract user file source from traceback, finding the actual error source.
    
    Traces through the stack to find the first user file that's NOT infrastructure,
    which is where the actual error originated.
    """
    if not tb:
        return ""
    
    # First pass: find all user files
    user_frames = []
    for frame in reversed(tb):
        if _is_user_file(frame.filename):
            user_frames.append(frame)
    
    # Second pass: skip infrastructure files to find actual error source
    for frame in user_frames:
        if not _is_infrastructure_file(frame.filename):
            try:
                rel_path = Path(frame.filename).relative_to(API_BASE_PATH)
                return f"{str(rel_path).replace(chr(92), '/')}:{frame.lineno}"
            except ValueError:
                return f"{Path(frame.filename).name}:{frame.lineno}"
    
    # Fallback: if all are infrastructure, return the first user file
    if user_frames:
        frame = user_frames[0]
        try:
            rel_path = Path(frame.filename).relative_to(API_BASE_PATH)
            return f"{str(rel_path).replace(chr(92), '/')}:{frame.lineno}"
        except ValueError:
            return f"{Path(frame.filename).name}:{frame.lineno}"
    
    return ""


def get_error_source() -> str:
    """Extract the source file and line from traceback."""
    stack = traceback.extract_stack()
    
    for frame in reversed(stack):
        if _is_user_file(frame.filename):
            try:
                rel_path = Path(frame.filename).relative_to(API_BASE_PATH)
                return f"{str(rel_path).replace(chr(92), '/')}:{frame.lineno}"
            except ValueError:
                return f"{Path(frame.filename).name}:{frame.lineno}"
    
    return ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_uvicorn_logging()
    logger.info("Starting API server...")
    
    # Check database connection
    db_connected = await check_database_connection()
    if not db_connected:
        logger.warning("Server running without database connection")
    
    # Start the crawl scheduler
    from app.services.scheduler_service import SchedulerService
    SchedulerService.start()
    logger.info("Crawl scheduler started")
    
    logger.success("API server started successfully")
    logger.info(f"Docs available at http://{settings.API_HOST}:{settings.API_PORT}/docs")
    yield
    # Shutdown
    logger.info("API server shutting down...")
    SchedulerService.stop()
    logger.info("Crawl scheduler stopped")


app = FastAPI(
    title="Chatbot API",
    description="Embeddable AI Chatbot SaaS API",
    version="1.0.0",
    lifespan=lifespan,
)


# ============== Exception Handlers ==============

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions with clean logging."""
    source = f"{exc.source_file}:{exc.source_line}"
    logger.error(f"{exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "detail": exc.short_detail,
            "source": source,
        },
        headers=exc.headers,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle standard HTTP exceptions."""
    # Print full error traceback if available
    if exc.__traceback__:
        import traceback as tb_module
        full_traceback = "".join(tb_module.format_exception(type(exc), exc, exc.__traceback__))
        print(full_traceback, end="")
    
    # Extract source from traceback (only user files)
    tb = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ else None
    source = get_user_source_from_traceback(tb) if tb else ""
    
    logger.error(f"{exc.detail}")
    
    response_content = {
        "success": False,
        "error": exc.detail,
        "detail": str(exc.detail),
    }
    if source:
        response_content["source"] = source
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with clean messages."""
    errors = exc.errors()
    
    # Create a clean error message
    error_messages = []
    for err in errors:
        loc = " → ".join(str(x) for x in err["loc"])
        error_messages.append(f"{loc}: {err['msg']}")
    
    message = "; ".join(error_messages) if error_messages else "Validation failed"
    short_msg = error_messages[0] if error_messages else "Invalid input"
    
    logger.error(f"Validation: {short_msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "detail": message,
            "fields": [{"field": " → ".join(str(x) for x in e["loc"]), "message": e["msg"]} for e in errors],
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database/SQLAlchemy exceptions with clean messages."""
    # Extract source from traceback (find actual error source, not infrastructure)
    tb = traceback.extract_tb(exc.__traceback__)
    source = get_user_source_from_traceback(tb)
    
    # Print full error traceback first
    import traceback as tb_module
    full_traceback = "".join(tb_module.format_exception(type(exc), exc, exc.__traceback__))
    print(full_traceback, end="")
    
    error_msg = str(exc)
    
    # Create user-friendly error messages
    if "password authentication failed" in error_msg.lower():
        user_msg = "Database authentication failed - check credentials"
        detail = "Unable to connect to database. Please verify your database credentials."
    elif "connection refused" in error_msg.lower() or "could not connect" in error_msg.lower():
        user_msg = "Database connection failed - is PostgreSQL running?"
        detail = "Unable to reach the database server. Please ensure PostgreSQL is running."
    elif "does not exist" in error_msg.lower():
        user_msg = "Database not found"
        detail = "The specified database does not exist. Please run migrations to create it."
    elif isinstance(exc, IntegrityError):
        user_msg = "Database integrity error"
        detail = "A database constraint was violated. This may indicate duplicate or invalid data."
    elif isinstance(exc, OperationalError):
        user_msg = "Database operation failed"
        detail = "A database operation could not be completed."
    else:
        user_msg = "Database error"
        detail = "An error occurred while accessing the database."
    
    # Log with actual source file
    if source:
        # Use extra to pass the actual source file location
        logger.error(f"{user_msg}", extra={"actual_source": source})
    else:
        logger.error(f"{user_msg}")
    
    response_content = {
        "success": False,
        "error": user_msg,
        "detail": detail,
    }
    if source:
        response_content["source"] = source
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=response_content,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    # Skip if it's a SQLAlchemy error (should be caught by database handler)
    if isinstance(exc, SQLAlchemyError):
        return await database_exception_handler(request, exc)
    
    # Print full error traceback first
    import traceback as tb_module
    full_traceback = "".join(tb_module.format_exception(type(exc), exc, exc.__traceback__))
    print(full_traceback, end="")
    
    # Extract source from traceback (find actual error source, not infrastructure)
    tb = traceback.extract_tb(exc.__traceback__)
    source = get_user_source_from_traceback(tb)
    
    # Log with actual source file
    if source:
        # Use extra to pass the actual source file location
        logger.error(f"Unexpected: {str(exc)[:100]}", extra={"actual_source": source})
    else:
        logger.error(f"Unexpected: {str(exc)[:100]}")
    
    response_content = {
        "success": False,
        "error": "Internal Server Error",
        "detail": str(exc) if settings.API_HOST == "0.0.0.0" else "An unexpected error occurred",
    }
    if source:
        response_content["source"] = source
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content,
    )


# ============== Middleware ==============

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all requests with timing information."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (time.time() - start_time) * 1000  # ms
    
    # Get status info
    status_code = response.status_code
    method = request.method
    path = request.url.path
    
    # Skip health checks and docs from logging
    if path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return response
    
    # Log based on status code
    if status_code >= 500:
        logger.error(f"{method} {path} → {status_code} ({duration:.0f}ms)")
    elif status_code >= 400:
        logger.warning(f"{method} {path} → {status_code} ({duration:.0f}ms)")
    else:
        logger.info(f"{method} {path} → {status_code} ({duration:.0f}ms)")
    
    return response


# CORS middleware
logger.info(f"CORS origins: {settings.CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.CORS_ORIGINS,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatbot-api"}

