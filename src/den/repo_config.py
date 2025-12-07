"""Repo configuration module for reading organization settings.

This module handles reading the default organization configuration from the config.json file
at ~/.config/den/config.json for use in repository creation.
"""

import json
from pathlib import Path
from typing import Optional


def get_config_file_path() -> Path:
    """Return the path to the config.json file.

    Returns:
      Path to ~/.config/den/config.json
    """
    return Path.home() / ".config" / "den" / "config.json"


def get_default_org() -> Optional[str]:
    """Read default_org from ~/.config/den/config.json.

    Reads the organization from the nested structure: {"repo": {"default_org": "..."}}.
    If the file does not exist, contains invalid JSON, or lacks the nested
    repo.default_org key, returns None.

    Returns:
      The configured organization string, or None if not configured.
    """
    config_file = get_config_file_path()

    if not config_file.exists():
        return None

    try:
        with config_file.open("r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return None
            config = json.loads(content)
    except (json.JSONDecodeError, OSError):
        return None

    repo_config = config.get("repo", {})
    if not isinstance(repo_config, dict):
        return None
    return repo_config.get("default_org")
