"""
BioEval Logging Utility

Provides consistent logging across the package.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from bioeval.config import LOG_FORMAT, LOG_DATE_FORMAT, DEFAULT_LOG_LEVEL


def setup_logger(
    name: str = "bioeval",
    level: str = DEFAULT_LOG_LEVEL,
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console: Whether to log to console
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "bioeval") -> logging.Logger:
    """Get or create a logger by name."""
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set up default
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


# Package-level logger
logger = get_logger("bioeval")


class LoggerMixin:
    """Mixin class to add logging to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(f"bioeval.{self.__class__.__name__}")


# Progress logging helper
class ProgressLogger:
    """Helper for logging progress of long-running operations."""
    
    def __init__(self, total: int, name: str = "Progress", log_every: int = 10):
        self.total = total
        self.name = name
        self.log_every = log_every
        self.current = 0
        self._logger = get_logger("bioeval.progress")
    
    def update(self, n: int = 1):
        """Update progress."""
        self.current += n
        if self.current % self.log_every == 0 or self.current == self.total:
            pct = (self.current / self.total) * 100
            self._logger.info(f"{self.name}: {self.current}/{self.total} ({pct:.1f}%)")
    
    def __enter__(self):
        self._logger.info(f"{self.name}: Starting (total: {self.total})")
        return self
    
    def __exit__(self, *args):
        self._logger.info(f"{self.name}: Complete")
