"""LaunchAgent management commands.

This module provides the launchctl command group for creating and managing
macOS LaunchAgent plist files through an interactive experience.
"""

import shlex

import typer

from den.launchctl_config import get_domain
from den.launchctl_runner import LaunchctlError, load_agent, unload_agent
from den.launchctl_validator import (
    validate_command,
    validate_hour,
    validate_interval,
    validate_minute,
    validate_task_name,
)
from den.plist_generator import TaskConfig, generate_plist
from den.plist_scanner import (
    build_plist_path,
    extract_task_name,
    get_launch_agents_dir,
    scan_domain_agents,
)

# Error message constants
_ERR_INVALID_INTEGER = "Error: Please enter a valid integer"

launchctl_app = typer.Typer(help="LaunchAgent management commands.")


def _prompt_task_name() -> str:
    """Prompt for task name with validation loop.

    Returns:
        Valid task name string.

    _Requirements: 1.1, 6.1, 6.2_
    """
    while True:
        name = typer.prompt("Task name")
        is_valid, error_msg = validate_task_name(name)
        if is_valid:
            return name
        typer.echo(f"Error: {error_msg}")


def _prompt_command() -> str:
    """Prompt for command to execute with validation loop.

    Returns:
        Valid command string.

    _Requirements: 1.2, 6.3_
    """
    while True:
        command = typer.prompt("Command to execute")
        is_valid, error_msg = validate_command(command)
        if is_valid:
            return command
        typer.echo(f"Error: {error_msg}")


def _prompt_schedule_type() -> str:
    """Prompt for scheduling type selection.

    Returns:
        Either 'interval' or 'calendar'.

    _Requirements: 1.3_
    """
    typer.echo("\nScheduling options:")
    typer.echo("  1. Interval (run every N seconds)")
    typer.echo("  2. Calendar (run at specific time daily)")

    while True:
        choice = typer.prompt("Select scheduling type (1 or 2)")
        if choice == "1":
            return "interval"
        elif choice == "2":
            return "calendar"
        typer.echo("Error: Please enter 1 or 2")


def _prompt_interval() -> int:
    """Prompt for interval duration with validation loop.

    Returns:
        Valid positive integer for interval seconds.

    _Requirements: 1.4, 6.4_
    """
    while True:
        try:
            seconds = int(typer.prompt("Interval in seconds"))
            is_valid, error_msg = validate_interval(seconds)
            if is_valid:
                return seconds
            typer.echo(f"Error: {error_msg}")
        except ValueError:
            typer.echo(_ERR_INVALID_INTEGER)


def _prompt_calendar() -> tuple[int, int]:
    """Prompt for calendar schedule (hour and minute) with validation loop.

    Returns:
        Tuple of (hour, minute).

    _Requirements: 1.5, 6.5, 6.6_
    """
    # Prompt for hour
    while True:
        try:
            hour = int(typer.prompt("Hour (0-23)"))
            is_valid, error_msg = validate_hour(hour)
            if is_valid:
                break
            typer.echo(f"Error: {error_msg}")
        except ValueError:
            typer.echo(_ERR_INVALID_INTEGER)

    # Prompt for minute
    while True:
        try:
            minute = int(typer.prompt("Minute (0-59)"))
            is_valid, error_msg = validate_minute(minute)
            if is_valid:
                break
            typer.echo(f"Error: {error_msg}")
        except ValueError:
            typer.echo(_ERR_INVALID_INTEGER)

    return hour, minute


@launchctl_app.command()
def install() -> None:
    """Create and load a new LaunchAgent through interactive prompts.

    _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 3.1, 3.2, 3.3_
    """
    # Get domain from config
    domain = get_domain()

    # Prompt for task configuration
    task_name = _prompt_task_name()
    command = _prompt_command()
    schedule_type = _prompt_schedule_type()

    # Get schedule values based on type
    start_interval: int | None = None
    start_calendar_hour: int | None = None
    start_calendar_minute: int | None = None

    if schedule_type == "interval":
        start_interval = _prompt_interval()
    else:
        start_calendar_hour, start_calendar_minute = _prompt_calendar()

    # Build label and config
    label = f"{domain}.{task_name}"
    program_arguments = shlex.split(command)

    config = TaskConfig(
        label=label,
        program_arguments=program_arguments,
        start_interval=start_interval,
        start_calendar_hour=start_calendar_hour,
        start_calendar_minute=start_calendar_minute,
        run_at_load=True,
    )

    # Generate plist content
    plist_content = generate_plist(config)

    # Ensure LaunchAgents directory exists
    launch_agents_dir = get_launch_agents_dir()
    launch_agents_dir.mkdir(parents=True, exist_ok=True)

    # Write plist file
    plist_path = build_plist_path(domain, task_name)
    try:
        plist_path.write_text(plist_content, encoding="utf-8")
    except OSError as e:
        typer.echo(f"Error: Failed to write plist file - {e}")
        raise typer.Exit(1)

    # Load the agent
    try:
        load_agent(plist_path)
        typer.echo(f"LaunchAgent installed successfully: {plist_path}")
    except LaunchctlError as e:
        typer.echo(f"Error: Failed to load agent - {e.stderr}")
        raise typer.Exit(1)


@launchctl_app.command()
def uninstall() -> None:
    """Unload and remove an existing LaunchAgent.

    _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
    """
    # Get domain from config
    domain = get_domain()

    # Scan for matching plist files
    matching_files = scan_domain_agents(domain)

    if not matching_files:
        typer.echo(f"No LaunchAgents found for domain '{domain}'")
        return

    # Display numbered list of available tasks
    typer.echo("\nAvailable LaunchAgents:")
    for i, plist_path in enumerate(matching_files, 1):
        task_name = extract_task_name(plist_path, domain)
        typer.echo(f"  {i}. {task_name}")

    # Prompt user to select task
    while True:
        try:
            choice = int(typer.prompt("\nSelect task to uninstall (number)"))
            if 1 <= choice <= len(matching_files):
                break
            typer.echo(
                f"Error: Please enter a number between 1 and {len(matching_files)}"
            )
        except ValueError:
            typer.echo(_ERR_INVALID_INTEGER)

    selected_path = matching_files[choice - 1]
    selected_task = extract_task_name(selected_path, domain)

    # Unload the agent
    try:
        unload_agent(selected_path)
    except LaunchctlError as e:
        typer.echo(f"Error: Failed to unload agent - {e.stderr}")
        raise typer.Exit(1)

    # Delete the plist file
    try:
        selected_path.unlink()
        typer.echo(f"LaunchAgent '{selected_task}' uninstalled successfully")
    except OSError as e:
        typer.echo(f"Error: Failed to delete plist file - {e}")
        raise typer.Exit(1)
