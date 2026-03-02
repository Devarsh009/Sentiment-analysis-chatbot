"""
Logging System
================
Centralized logging configuration for the application.

Features:
- Console output with colored formatting
- File output for persistent logs
- Configurable log levels
- Structured log format with timestamps
"""

import os
import sys
import logging
from datetime import datetime


# ─── Custom Formatter ────────────────────────────────────────────────────────
class ColoredFormatter(logging.Formatter):
    """
    Custom log formatter that adds colors to console output.
    Makes it easy to visually distinguish log levels.
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record):
        """Add color to the log level name."""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(level: str = "INFO", log_file: str = "app.log"):
    """
    Configure the application-wide logging system.
    
    Sets up two handlers:
    1. Console handler (with colors) - for development
    2. File handler - for production/debugging
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # ── Console Handler ──
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    console_format = ColoredFormatter(
        fmt="%(asctime)s │ %(levelname)-18s │ %(name)s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # ── File Handler ──
    log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "."
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    
    file_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("datasets").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger instance.
    
    Usage:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Hello!")
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured Logger instance
    """
    return logging.getLogger(name)
