"""Unit tests for the repo config module.

Tests for config reading functions including path resolution,
default org loading with various file states.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from den.repo_config import (
    get_config_file_path,
    get_default_org,
)


def test_get_config_file_path_returns_correct_path():
    """Test that get_config_file_path returns ~/.config/den/config.json."""
    result = get_config_file_path()
    expected = Path.home() / ".config" / "den" / "config.json"
    assert result == expected


def test_get_default_org_returns_none_for_missing_file():
    """Test that get_default_org returns None when config file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent_file = Path(tmpdir) / "nonexistent" / "config.json"

        with patch(
            "den.repo_config.get_config_file_path", return_value=nonexistent_file
        ):
            result = get_default_org()
            assert result is None


def test_get_default_org_returns_none_for_empty_file():
    """Test that get_default_org returns None when config file is empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        config_file.write_text("")

        with patch("den.repo_config.get_config_file_path", return_value=config_file):
            result = get_default_org()
            assert result is None


def test_get_default_org_returns_configured_value():
    """Test that get_default_org returns org from valid config file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        config_file.write_text(json.dumps({"repo": {"default_org": "my-org"}}))

        with patch("den.repo_config.get_config_file_path", return_value=config_file):
            result = get_default_org()
            assert result == "my-org"


def test_get_default_org_returns_none_for_invalid_json():
    """Test that get_default_org returns None when config file has invalid JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        config_file.write_text("{ invalid json }")

        with patch("den.repo_config.get_config_file_path", return_value=config_file):
            result = get_default_org()
            assert result is None


def test_get_default_org_returns_none_when_repo_key_missing():
    """Test that get_default_org returns None when repo key is absent."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        config_file.write_text(json.dumps({"other_key": "value"}))

        with patch("den.repo_config.get_config_file_path", return_value=config_file):
            result = get_default_org()
            assert result is None


def test_get_default_org_returns_none_when_default_org_key_missing():
    """Test that get_default_org returns None when default_org key is absent."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        config_file.write_text(json.dumps({"repo": {"other": "value"}}))

        with patch("den.repo_config.get_config_file_path", return_value=config_file):
            result = get_default_org()
            assert result is None


def test_get_default_org_returns_none_when_repo_not_dict():
    """Test that get_default_org returns None when repo is not a dict."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        config_file.write_text(json.dumps({"repo": "not a dict"}))

        with patch("den.repo_config.get_config_file_path", return_value=config_file):
            result = get_default_org()
            assert result is None
