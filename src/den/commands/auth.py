"""
Authentication Management Module.

This module provides commands for managing API keys and other credentials used by the CLI.
It handles secure storage of secrets in a configuration file.

Key Features:
- Secure storage: Keys are saved with 600 file permissions.
- Centralized config: Credential configuration is stored in ~/.config/den/config.json.
"""

import json
from pathlib import Path
from typing import Any, Dict

import typer
from rich.console import Console

# Initialize the auth sub-application
app = typer.Typer(name="auth", help="Manage authentication credentials.")
console = Console()

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "den"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_general_config() -> Dict[str, Any]:
    """
    Load the general configuration from the JSON file.

    Returns:
        Dict[str, Any]: The configuration dictionary. Returns an empty dict if
                        the file doesn't exist or is invalid JSON.
    """
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_general_config(config: Dict[str, Any]) -> None:
    """
    Save the general configuration to the JSON file.

    This function ensures the configuration directory exists and sets
    restrictive file permissions (600 - read/write only by owner)
    to protect sensitive data like API keys.

    Args:
        config (Dict[str, Any]): The configuration dictionary to save.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    # Ensure privacy: Read/Write for owner only
    CONFIG_FILE.chmod(0o600)


@app.command()
def anthropic():
    """
    Prompt for and save the Anthropic API key.

    This interactive command asks the user to input their Anthropic API key.
    The input is hidden for security. The key is then validated (basic prefix check)
    and stored in the central configuration file.
    """
    key = typer.prompt("Enter your Anthropic API Key", hide_input=True)

    # Basic validation to help users avoid copy-paste errors
    if not key.startswith("sk-"):
        console.print("[yellow]Warning: Key does not start with 'sk-'.[/yellow]")

    config = get_general_config()
    config["anthropic_api_key"] = key
    save_general_config(config)
    console.print(f"[green]API Key saved to {CONFIG_FILE}[/green]")
