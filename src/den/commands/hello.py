"""
Hello Command Module.

This module implements a basic 'hello' command to demonstrate Typer and Rich integration.
It serves as a simple example of a command definition without a sub-application structure.
"""

import typer
from rich.console import Console

# Initialize Rich console for formatted output
console = Console()


def hello(name: str = typer.Argument("World", help="Name to greet")):
    """
    Say hello to someone.

    This command prints a friendly greeting to the console using Rich's formatting capabilities.

    Args:
        name (str): The name of the person to greet. Defaults to "World".
                    This argument is optional in the CLI.
    """
    # Print with Rich styling: bold green text
    console.print(f"[bold green]Hello {name}![/bold green]")
