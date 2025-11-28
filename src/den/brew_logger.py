"""Brew logger module for logging brew upgrade operations.

This module configures logging for the brew upgrade process, writing logs
to ~/.config/den/logs/brew-upgrade.log with timestamps and log levels.
"""

import logging
from pathlib import Path


def get_log_file_path() -> Path:
    """Return the path to the brew-upgrade.log file.

    Returns:
        Path to ~/.config/den/logs/brew-upgrade.log
    """
    return Path.home() / ".config" / "den" / "logs" / "brew-upgrade.log"


def setup_brew_logger() -> logging.Logger:
    """Configure and return logger for brew operations.

    Creates the log directory if it doesn't exist and configures a file handler
    with timestamp and level format.

    Returns:
        Configured logger instance for brew operations.

    Raises:
        OSError: If log directory cannot be created.
    """
    logger = logging.getLogger("den.brew")

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Create log directory if it doesn't exist
    log_file = get_log_file_path()
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Configure file handler with timestamp and level format
    # Format: "2025-01-15 10:30:45 INFO: Message"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
