"""State storage functions for persisting application state.

This module handles reading and writing application state to the state.json file
at ~/.config/den/state.json. State is organized by feature keys (e.g., "brew").
"""

import json
from pathlib import Path
from typing import Any


def get_state_file_path() -> Path:
    """Return the path to the state.json file.

    Returns:
        Path to ~/.config/den/state.json
    """
    return Path.home() / ".config" / "den" / "state.json"


def load_state() -> dict[str, Any]:
    """Load existing state from state.json.

    Returns:
        Dictionary of state, or empty dict if file doesn't exist.
        If the file contains invalid JSON, returns empty dict.
    """
    state_file = get_state_file_path()
    if not state_file.exists():
        return {}

    try:
        with state_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Per error handling spec: treat invalid JSON as empty state
        return {}


def save_state(state: dict[str, Any]) -> None:
    """Save state to state.json, merging with existing content.

    This function merges the provided state with any existing state,
    preserving keys that are not in the new state.

    Args:
        state: Dictionary of state to save/merge.

    Raises:
        OSError: If directory or file cannot be created/written.
    """
    state_file = get_state_file_path()
    state_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing state and merge
    existing_state = load_state()
    existing_state.update(state)

    with state_file.open("w", encoding="utf-8") as f:
        json.dump(existing_state, f, indent=2)


def get_brew_state() -> dict[str, str] | None:
    """Get the brew-specific state (hash, gist_id).

    Returns:
        Dictionary with brew state containing 'brewfile_hash' and/or 'gist_id',
        or None if no brew state exists.
    """
    state = load_state()
    return state.get("brew")


def save_brew_state(brewfile_hash: str, gist_id: str) -> None:
    """Save brew-specific state under the 'brew' key.

    Args:
        brewfile_hash: The SHA-256 hash of the Brewfile content.
        gist_id: The GitHub Gist ID for the backup.

    Raises:
        OSError: If directory or file cannot be created/written.
    """
    brew_state = {
        "brewfile_hash": brewfile_hash,
        "gist_id": gist_id,
    }
    save_state({"brew": brew_state})
