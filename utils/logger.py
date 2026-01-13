"""
Logger Utility
Configures and provides logging functionality for the framework.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from config.settings import settings


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # Add color to level name
        record.levelname = f"{color}{record.levelname}{reset}"

        return super().format(record)


def setup_logger(
    name: str = "automation",
    level: str = None,
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: Path = None,
) -> logging.Logger:
    """
    Setup and configure a logger.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to write logs to file
        log_to_console: Whether to output logs to console
        log_dir: Directory for log files

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Set log level
    level = level or settings.LOG_LEVEL
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        log_dir = log_dir or settings.REPORTS_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{name}_{timestamp}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(settings.LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.

    """
    if name is None:
        name = "automation"
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin class to add logging capability to any class.

    """

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger


# Initialize root logger
def init_logging(level: str = None) -> None:
    """Initialize framework logging."""
    setup_logger("automation", level=level)
    setup_logger("playwright", level="WARNING")  # Reduce Playwright noise
