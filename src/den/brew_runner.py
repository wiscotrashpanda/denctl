"""Brew runner module for executing Homebrew commands.

This module handles execution of Homebrew commands including brew upgrade
and brew bundle dump for generating Brewfiles.
"""

import subprocess


class BrewCommandError(Exception):
    """Exception raised when a Homebrew command fails."""

    def __init__(self, command: str, returncode: int, stderr: str):
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"Command '{command}' failed with code {returncode}: {stderr}")


def run_brew_upgrade() -> None:
    """Execute brew upgrade command to update all installed packages.

    Raises:
        BrewCommandError: If brew upgrade fails.
    """
    try:
        result = subprocess.run(
            ["brew", "upgrade"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise BrewCommandError("brew upgrade", result.returncode, result.stderr)
    except FileNotFoundError as e:
        raise BrewCommandError("brew upgrade", -1, "brew command not found") from e


def generate_brewfile() -> str:
    """Execute brew bundle dump and return Brewfile content.

    Returns:
        The Brewfile content as a string.

    Raises:
        BrewCommandError: If brew bundle dump fails.
    """
    try:
        result = subprocess.run(
            ["brew", "bundle", "dump", "--force", "--stdout"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise BrewCommandError(
                "brew bundle dump --force --stdout", result.returncode, result.stderr
            )
        return result.stdout
    except FileNotFoundError as e:
        raise BrewCommandError(
            "brew bundle dump --force --stdout", -1, "brew command not found"
        ) from e
