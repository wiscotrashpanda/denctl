"""Unit tests for the auth storage module.

Tests for auth storage functions including path resolution,
credential loading, and directory creation.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from den.auth_storage import (
    get_auth_file_path,
    load_credentials,
    save_credential,
)


def test_get_auth_file_path_returns_correct_path():
    """Test that get_auth_file_path returns ~/.config/den/auth.json.

    _Requirements: 3.1_
    """
    result = get_auth_file_path()
    expected = Path.home() / ".config" / "den" / "auth.json"
    assert result == expected


def test_load_credentials_returns_empty_dict_for_missing_file():
    """Test that load_credentials returns empty dict when file doesn't exist.

    _Requirements: 3.3_
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent_file = Path(tmpdir) / "nonexistent" / "auth.json"

        with patch(
            "den.auth_storage.get_auth_file_path", return_value=nonexistent_file
        ):
            result = load_credentials()
            assert result == {}


def test_save_credential_creates_directory_if_needed():
    """Test that save_credential creates the config directory if it doesn't exist.

    _Requirements: 3.2_
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        auth_file = Path(tmpdir) / "new_dir" / "subdir" / "auth.json"

        with patch("den.auth_storage.get_auth_file_path", return_value=auth_file):
            save_credential("test_key", "test_value")

            # Verify directory was created
            assert auth_file.parent.exists()
            # Verify file was created with correct content
            assert auth_file.exists()
            result = load_credentials()
            assert result == {"test_key": "test_value"}
