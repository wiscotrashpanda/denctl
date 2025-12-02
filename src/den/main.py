"""Main entry point for the den CLI application.

This module initializes the Typer application and registers all commands.
"""

import typer

from den import __version__
from den.commands.auth import auth_app
from den.commands.brew import brew_app
from den.commands.hello import hello, hello_again
from den.commands.launchctl import launchctl_app

app = typer.Typer(
  name="den",
  help="A CLI utility for local machine automations.",
  add_completion=False,
)

# Register commands
app.command()(hello)
app.command(name="hello-again")(hello_again)
app.add_typer(auth_app, name="auth")
app.add_typer(brew_app, name="brew")
app.add_typer(launchctl_app, name="launchctl")


def version_callback(value: bool) -> None:
  """Display the application version and exit.

  Args:
    value: If True, print version and raise Exit.
  """
  if value:
    typer.echo(f"den version {__version__}")
    raise typer.Exit()


@app.callback()
def main(
  version: bool = typer.Option(
    False,
    "--version",
    "-v",
    help="Show the application version and exit.",
    callback=version_callback,
    is_eager=True,
  ),
) -> None:
  """den - A CLI utility for local machine automations."""
  pass
