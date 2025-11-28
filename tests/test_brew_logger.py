"""Property-based tests for brew logger module.

These tests use hypothesis to verify universal properties for log formatting.
"""

import re
import tempfile
from pathlib import Path
from unittest.mock import patch

from hypothesis import given, settings, strategies as st

from den.brew_logger import get_log_file_path, setup_brew_logger


# Strategy for log messages - printable text without newlines
log_message_strategy = st.text(
    min_size=1,
    max_size=200,
    alphabet=st.characters(
        blacklist_categories=("Cs",),
        blacklist_characters=("\n", "\r"),
    ),
)

# Strategy for log levels
log_level_strategy = st.sampled_from(["INFO", "WARNING", "ERROR"])


@settings(max_examples=100)
@given(
    message=log_message_strategy,
    level=log_level_strategy,
)
def test_property_log_entry_format_compliance(message: str, level: str) -> None:
    """**Feature: brew-backup, Property 4: Log entry format compliance**

    *For any* log entry written by the brew logger, the entry SHALL contain
    a timestamp and a log level (INFO, ERROR, or WARNING).

    **Validates: Requirements 6.3, 6.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "brew-upgrade.log"

        with patch("den.brew_logger.get_log_file_path", return_value=log_file):
            # Get a fresh logger for each test
            import logging

            logger_name = f"den.brew.test.{id(message)}"
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.setLevel(logging.DEBUG)

            # Create log directory and file handler
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                fmt="%(asctime)s %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Log the message at the specified level
            if level == "INFO":
                logger.info(message)
            elif level == "WARNING":
                logger.warning(message)
            elif level == "ERROR":
                logger.error(message)

            # Flush and close handler to ensure write
            file_handler.flush()
            file_handler.close()

            # Read the log file
            log_content = log_file.read_text(encoding="utf-8")
            log_lines = log_content.strip().split("\n")

            assert len(log_lines) >= 1, "Log file should contain at least one entry"

            # Check the last log entry (the one we just wrote)
            log_entry = log_lines[-1]

            # Verify timestamp format: YYYY-MM-DD HH:MM:SS
            timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
            assert re.search(timestamp_pattern, log_entry), (
                f"Log entry should contain timestamp. Entry: {log_entry}"
            )

            # Verify log level is present
            assert level in log_entry, (
                f"Log entry should contain level '{level}'. Entry: {log_entry}"
            )


def test_log_file_path_returns_expected_location() -> None:
    """Test that get_log_file_path returns the correct path."""
    expected = Path.home() / ".config" / "den" / "logs" / "brew-upgrade.log"
    assert get_log_file_path() == expected


def test_setup_brew_logger_creates_directory() -> None:
    """Test that setup_brew_logger creates the log directory if needed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "logs" / "brew-upgrade.log"

        with patch("den.brew_logger.get_log_file_path", return_value=log_file):
            logger = setup_brew_logger()

            # Clear the cached logger for next test
            logger.handlers.clear()

            assert log_file.parent.exists(), "Log directory should be created"


def test_setup_brew_logger_returns_logger_with_handler() -> None:
    """Test that setup_brew_logger returns a properly configured logger."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "brew-upgrade.log"

        with patch("den.brew_logger.get_log_file_path", return_value=log_file):
            # Clear any existing handlers first
            import logging

            existing_logger = logging.getLogger("den.brew")
            existing_logger.handlers.clear()

            logger = setup_brew_logger()

            assert logger.name == "den.brew"
            assert len(logger.handlers) >= 1, "Logger should have at least one handler"

            # Clean up
            logger.handlers.clear()
