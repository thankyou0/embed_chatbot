"""
Professional logging configuration for the Chatbot API.
Provides clean, readable logs with file location and short messages.
Only shows source paths from user-created project files.
"""
import logging
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Optional

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


class CleanFormatter(logging.Formatter):
    """Custom formatter that produces clean, readable log output."""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.GRAY,
        logging.INFO: Colors.CYAN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED + Colors.BOLD,
    }
    
    # ASCII-safe icons for Windows compatibility
    LEVEL_ICONS = {
        logging.DEBUG: "o",
        logging.INFO: "*",
        logging.WARNING: "!",
        logging.ERROR: "X",
        logging.CRITICAL: "X",
    }
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors
        self.base_path = Path(__file__).parent.parent.parent  # apps/api directory
    
    def _get_relative_path(self, pathname: str) -> str:
        """Get relative path from the api directory."""
        try:
            path = Path(pathname)
            try:
                rel_path = str(path.relative_to(self.base_path))
                # Clean up the path for display
                return rel_path.replace("\\", "/")
            except ValueError:
                # If can't get relative path (e.g. library file), just use filename
                return path.name
        except Exception:
            return pathname
    
    def format(self, record: logging.LogRecord) -> str:
        # Get timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Get level info
        level_color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        level_icon = self.LEVEL_ICONS.get(record.levelno, "*")
        level_name = record.levelname.ljust(8)
        
        # Check if actual_source was passed in extra (from exception handlers)
        actual_source = getattr(record, 'actual_source', None)
        
        if actual_source:
            # Use the actual source from traceback analysis
            rel_path = actual_source
            line_no = ""  # Source already includes line number
        else:
            # Get file location
            rel_path = self._get_relative_path(record.pathname)
            line_no = f":{record.lineno}"
        
        # Format message
        message = record.getMessage()
        
        if self.use_colors:
            # Colored output for terminal
            return (
                f"{Colors.GRAY}{timestamp}{Colors.RESET} "
                f"{level_color}[{level_icon}] {level_name}{Colors.RESET} "
                f"{Colors.GRAY}|{Colors.RESET} {message}\n"
                f"{Colors.GRAY}              -> {rel_path}{line_no}{Colors.RESET}"
            )
        else:
            # Plain output (for file logging)
            return (
                f"{timestamp} [{level_icon}] {level_name} | {message}\n"
                f"              -> {rel_path}{line_no}"
            )


class SuccessAdapter(logging.LoggerAdapter):
    """Logger adapter that adds a success method."""
    
    def success(self, msg: str, *args, **kwargs):
        """Log a success message (uses INFO level with special formatting)."""
        # Add success marker to extra
        kwargs.setdefault('extra', {})
        kwargs['extra']['is_success'] = True
        self.info(msg, *args, **kwargs)


class SuccessFormatter(CleanFormatter):
    """Formatter that handles success messages specially."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Check if this is a success message
        is_success = getattr(record, 'is_success', False)
        
        if is_success and self.use_colors:
            # Get timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            rel_path = self._get_relative_path(record.pathname)
            message = record.getMessage()
            
            return (
                f"{Colors.GRAY}{timestamp}{Colors.RESET} "
                f"{Colors.GREEN}[+] SUCCESS {Colors.RESET} "
                f"{Colors.GRAY}|{Colors.RESET} {message}\n"
                f"{Colors.GRAY}              -> {rel_path}:{record.lineno}{Colors.RESET}"
            )
        
        return super().format(record)


def get_logger(name: str, use_colors: bool = True) -> SuccessAdapter:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        use_colors: Whether to use colored output
    
    Returns:
        Configured logger with success() method
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Console handler with UTF-8 encoding for Windows compatibility
        stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        console_handler = logging.StreamHandler(stream)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(SuccessFormatter(use_colors=use_colors))
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return SuccessAdapter(logger, {})


def setup_uvicorn_logging():
    """Configure uvicorn logging to match our format."""
    # Get uvicorn loggers
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_error = logging.getLogger("uvicorn.error")
    
    # Clear existing handlers
    for log in [uvicorn_logger, uvicorn_access, uvicorn_error]:
        log.handlers.clear()
        log.setLevel(logging.INFO)
    
    # Disable uvicorn.access from terminal (keep it silent)
    uvicorn_access.disabled = True
    
    # Add our formatter with UTF-8 encoding for Windows compatibility
    stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    handler = logging.StreamHandler(stream)
    handler.setFormatter(SuccessFormatter(use_colors=True))
    
    uvicorn_logger.addHandler(handler)
    # uvicorn_access.addHandler(handler)  # Don't add handler - keep access logs silent
    uvicorn_error.addHandler(handler)


# Create a default logger for quick imports
logger = get_logger("chatbot_api")
