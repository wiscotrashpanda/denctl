"""
Main Entry Point for den.

This module initializes the Typer application, registers all available subcommands,
and handles global options like `--version`.

The application structure is modular:
- The main `app` object serves as the root.
- Subcommands (like `hello`) are directly attached.
- Command groups (like `homebrew` and `auth`) are added using `add_typer`.

Usage:
    This file is executed when running the CLI.
    Example: `uv run den --help`
"""

from typing import Optional

import typer
from rich import print

from den import __version__
from den.commands import auth, homebrew
from den.commands.hello import hello

# Initialize the main Typer application
# - name: The name of the CLI (displayed in help).
# - help: The description displayed in the main help output.
# - no_args_is_help: If true, running without arguments shows help instead of error.
app = typer.Typer(
    name="den",
    help="den - 🦝 automation CLI",
    no_args_is_help=True,
)

# --- Command Registration ---
# Register the simple 'hello' command
app.command(name="hello")(hello)

# Register the 'homebrew' command group
# This adds all commands defined in the homebrew module under the 'homebrew' subcommand.
app.add_typer(homebrew.app, name="homebrew")

# Register the 'auth' command group
# This adds all commands defined in the auth module under the 'auth' subcommand.
app.add_typer(auth.app, name="auth")


def version_callback(value: bool):
    """
    Callback function for the --version option.

    If the flag is present, it prints the current version (from __init__.py)
    using Rich for formatting, and then exits the application.

    Args:
        value (bool): The value of the flag (True if present).
    """
    if value:
        print(f"den version: [bold blue]{__version__}[/bold blue]")
        raise typer.Exit()


@app.callback()
def common(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        help="Show version and exit.",
    ),
):
    """
    Common callback for the main application.

    This function is executed before any command. It defines global options
    that apply to the entire CLI, such as --version.

    Args:
        ctx (typer.Context): The Typer context object (unused here but available).
        version (bool): The --version flag trigger.
    """
    pass


def main() -> None:
    """
    Programmatic entry point for the application.
    Calls the Typer app object to parse arguments and execute commands.
    """
    app()


if __name__ == "__main__":
    main()
