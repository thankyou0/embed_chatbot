"""
Custom exceptions and error responses for the Chatbot API.
Provides clean, consistent error handling with proper logging.
"""
from typing import Optional, Any, Dict
from fastapi import HTTPException, status
import traceback
from pathlib import Path


class APIException(HTTPException):
    """
    Base exception for API errors.
    Automatically captures file location for logging.
    """
    
    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.message = message
        self.short_detail = detail or message
        
        # Capture the file and line where exception was raised
        stack = traceback.extract_stack()
        # Get the caller's frame (skip this __init__ and the frame that called it)
        for frame in reversed(stack[:-1]):
            if "exceptions.py" not in frame.filename:
                self.source_file = Path(frame.filename).name
                self.source_line = frame.lineno
                break
        else:
            self.source_file = "unknown"
            self.source_line = 0
        
        super().__init__(status_code=status_code, detail=message, headers=headers)


class BadRequestError(APIException):
    """400 Bad Request"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            detail=detail,
        )


class UnauthorizedError(APIException):
    """401 Unauthorized"""
    def __init__(self, message: str = "Authentication required", detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(APIException):
    """403 Forbidden"""
    def __init__(self, message: str = "Access denied", detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            detail=detail,
        )


class NotFoundError(APIException):
    """404 Not Found"""
    def __init__(self, message: str = "Resource not found", detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            detail=detail,
        )


class ConflictError(APIException):
    """409 Conflict"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            detail=detail,
        )


class ValidationError(APIException):
    """422 Validation Error"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            detail=detail,
        )


class InternalError(APIException):
    """500 Internal Server Error"""
    def __init__(self, message: str = "Internal server error", detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            detail=detail,
        )


class DatabaseError(APIException):
    """Database-related errors"""
    def __init__(self, message: str = "Database error", detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            detail=detail,
        )


# Error response model for API documentation
ERROR_RESPONSES = {
    400: {"description": "Bad Request", "content": {"application/json": {"example": {"success": False, "error": "Bad request", "message": "Invalid input data", "source": "auth.py:42"}}}},
    401: {"description": "Unauthorized", "content": {"application/json": {"example": {"success": False, "error": "Unauthorized", "message": "Invalid credentials", "source": "auth.py:56"}}}},
    403: {"description": "Forbidden", "content": {"application/json": {"example": {"success": False, "error": "Forbidden", "message": "Access denied", "source": "auth.py:78"}}}},
    404: {"description": "Not Found", "content": {"application/json": {"example": {"success": False, "error": "Not Found", "message": "Resource not found", "source": "users.py:34"}}}},
    500: {"description": "Internal Server Error", "content": {"application/json": {"example": {"success": False, "error": "Internal Error", "message": "Something went wrong", "source": "service.py:120"}}}},
}

