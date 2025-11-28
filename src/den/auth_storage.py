"""Auth storage module for managing credentials.

This module handles reading and writing credentials to the auth.json file
at ~/.config/den/auth.json.
"""

import json
from pathlib import Path


def get_auth_file_path() -> Path:
    """Return the path to the auth.json file.

    Returns:
        Path to ~/.config/den/auth.json
    """
    return Path.home() / ".config" / "den" / "auth.json"


def load_credentials() -> dict[str, str]:
    """Load existing credentials from auth.json.

    Returns:
        Dictionary of credentials, or empty dict if file doesn't exist.

    Raises:
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    auth_file = get_auth_file_path()
    if not auth_file.exists():
        return {}

    with auth_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_credentials(credentials: dict[str, str]) -> None:
    """Save credentials to auth.json, creating directory if needed.

    Args:
        credentials: Dictionary of credentials to save.

    Raises:
        OSError: If directory or file cannot be created/written.
    """
    auth_file = get_auth_file_path()
    auth_file.parent.mkdir(parents=True, exist_ok=True)

    with auth_file.open("w", encoding="utf-8") as f:
        json.dump(credentials, f, indent=2)


def save_credential(key: str, value: str) -> None:
    """Save a single credential, preserving existing credentials.

    Args:
        key: The credential key (e.g., "anthropic_api_key").
        value: The credential value.

    Raises:
        OSError: If directory or file cannot be created/written.
        json.JSONDecodeError: If existing file contains invalid JSON.
    """
    credentials = load_credentials()
    credentials[key] = value
    save_credentials(credentials)
