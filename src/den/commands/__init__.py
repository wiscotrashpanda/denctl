"""
Command Modules for den.

This package contains the implementations for various CLI commands.
Each module typically defines a Typer app (sub-app) or a standalone command function.

Available Modules:
- hello: A simple greeting command.
- homebrew: Commands for managing Homebrew backups and configuration.
- auth: Commands for managing authentication credentials.
"""

from den.commands import auth, hello, homebrew

__all__ = ["auth", "hello", "homebrew"]
