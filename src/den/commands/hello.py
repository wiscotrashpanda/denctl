"""Hello command module for the den CLI.

This module provides the hello command for greeting users.
"""

import typer


def hello(
    name: str = typer.Option("World", "--name", "-n", help="Name to greet"),
) -> None:
    """Say hello to someone.

    Outputs a greeting message to the console in the format "Hello, {name}!".

    Args:
        name: The name to include in the greeting. Defaults to "World".
    """
    typer.echo(f"Hello, {name}!")
