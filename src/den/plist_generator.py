"""Plist generator module for LaunchAgent configuration.

This module provides functionality to generate and parse macOS LaunchAgent
plist XML files from TaskConfig dataclass instances.
"""

import plistlib
from dataclasses import dataclass


class PlistParseError(Exception):
    """Raised when plist content cannot be parsed."""

    pass


class PlistGenerationError(Exception):
    """Raised when plist content cannot be generated."""

    pass


@dataclass
class TaskConfig:
    """Configuration for a LaunchAgent task.

    Attributes:
        label: The unique identifier for the LaunchAgent (domain.task format).
        program_arguments: List of command and arguments to execute.
        start_interval: Interval in seconds between runs (mutually exclusive with calendar).
        start_calendar_hour: Hour (0-23) for calendar-based scheduling.
        start_calendar_minute: Minute (0-59) for calendar-based scheduling.
        run_at_load: Whether to run immediately when loaded.
        environment_variables: Dict of environment variables to set when executing.
    """

    label: str
    program_arguments: list[str]
    start_interval: int | None = None
    start_calendar_hour: int | None = None
    start_calendar_minute: int | None = None
    run_at_load: bool = True
    environment_variables: dict[str, str] | None = None


def generate_plist(config: TaskConfig) -> str:
    """Generate plist XML content from task configuration.

    Creates a valid macOS LaunchAgent plist XML string with proper DOCTYPE
    declaration and all required keys based on the TaskConfig.

    Args:
        config: The task configuration.

    Returns:
        Valid plist XML string.

    Raises:
        PlistGenerationError: If the config is invalid.

    _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
    """
    if not config.label:
        raise PlistGenerationError("Label cannot be empty")
    if not config.program_arguments:
        raise PlistGenerationError("Program arguments cannot be empty")

    plist_dict: dict = {
        "Label": config.label,
        "ProgramArguments": config.program_arguments,
        "RunAtLoad": config.run_at_load,
    }

    if config.environment_variables:
        plist_dict["EnvironmentVariables"] = config.environment_variables

    # Add scheduling - either interval or calendar-based
    if config.start_interval is not None:
        plist_dict["StartInterval"] = config.start_interval
    elif (
        config.start_calendar_hour is not None
        and config.start_calendar_minute is not None
    ):
        plist_dict["StartCalendarInterval"] = {
            "Hour": config.start_calendar_hour,
            "Minute": config.start_calendar_minute,
        }

    # Generate XML using plistlib
    xml_bytes = plistlib.dumps(plist_dict, fmt=plistlib.FMT_XML)
    return xml_bytes.decode("utf-8")


def parse_plist(content: str) -> TaskConfig:
    """Parse plist XML content into task configuration.

    Args:
        content: The plist XML string.

    Returns:
        TaskConfig parsed from the plist.

    Raises:
        PlistParseError: If the content is not valid plist XML.

    _Requirements: 5.7_
    """
    try:
        plist_dict = plistlib.loads(content.encode("utf-8"))
    except Exception as e:
        raise PlistParseError(f"Failed to parse plist XML: {e}") from e

    # Extract required fields
    label = plist_dict.get("Label")
    if not label:
        raise PlistParseError("Plist missing required 'Label' key")

    program_arguments = plist_dict.get("ProgramArguments")
    if not program_arguments:
        raise PlistParseError("Plist missing required 'ProgramArguments' key")

    run_at_load = plist_dict.get("RunAtLoad", True)
    environment_variables = plist_dict.get("EnvironmentVariables")

    # Extract scheduling
    start_interval = plist_dict.get("StartInterval")
    start_calendar_hour = None
    start_calendar_minute = None

    calendar_interval = plist_dict.get("StartCalendarInterval")
    if calendar_interval:
        start_calendar_hour = calendar_interval.get("Hour")
        start_calendar_minute = calendar_interval.get("Minute")

    return TaskConfig(
        label=label,
        program_arguments=program_arguments,
        start_interval=start_interval,
        start_calendar_hour=start_calendar_hour,
        start_calendar_minute=start_calendar_minute,
        run_at_load=run_at_load,
        environment_variables=environment_variables,
    )
