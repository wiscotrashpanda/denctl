"""Tests for the authentication module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from denctl.commands.auth import (
    CONFIG_DIR,
    CONFIG_FILE,
    app,
    get_general_config,
    save_general_config,
)

runner = CliRunner()


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Create a temporary config directory for testing."""
    temp_config = tmp_path / ".config" / "denctl"
    temp_config_file = temp_config / "config.json"

    # Patch the module-level constants
    monkeypatch.setattr("denctl.commands.auth.CONFIG_DIR", temp_config)
    monkeypatch.setattr("denctl.commands.auth.CONFIG_FILE", temp_config_file)

    return temp_config, temp_config_file


def test_get_general_config_no_file(temp_config_dir):
    """Test getting config when file doesn't exist."""
    config = get_general_config()
    assert config == {}


def test_get_general_config_empty_file(temp_config_dir):
    """Test getting config from empty file."""
    temp_config, temp_config_file = temp_config_dir
    temp_config.mkdir(parents=True, exist_ok=True)
    temp_config_file.write_text("")

    config = get_general_config()
    assert config == {}


def test_get_general_config_valid_file(temp_config_dir):
    """Test getting config from valid JSON file."""
    temp_config, temp_config_file = temp_config_dir
    temp_config.mkdir(parents=True, exist_ok=True)
    test_data = {"anthropic_api_key": "sk-test-key"}
    temp_config_file.write_text(json.dumps(test_data))

    config = get_general_config()
    assert config == test_data


def test_get_general_config_invalid_json(temp_config_dir):
    """Test getting config from file with invalid JSON."""
    temp_config, temp_config_file = temp_config_dir
    temp_config.mkdir(parents=True, exist_ok=True)
    temp_config_file.write_text("not valid json {")

    config = get_general_config()
    assert config == {}


def test_save_general_config_creates_directory(temp_config_dir):
    """Test that save_general_config creates directory if it doesn't exist."""
    temp_config, temp_config_file = temp_config_dir
    test_config = {"anthropic_api_key": "sk-test-key"}

    save_general_config(test_config)

    assert temp_config.exists()
    assert temp_config_file.exists()


def test_save_general_config_writes_json(temp_config_dir):
    """Test that save_general_config writes valid JSON."""
    temp_config, temp_config_file = temp_config_dir
    test_config = {"anthropic_api_key": "sk-test-key", "other_setting": "value"}

    save_general_config(test_config)

    saved_data = json.loads(temp_config_file.read_text())
    assert saved_data == test_config


def test_save_general_config_sets_permissions(temp_config_dir):
    """Test that save_general_config sets 600 permissions."""
    temp_config, temp_config_file = temp_config_dir
    test_config = {"anthropic_api_key": "sk-test-key"}

    save_general_config(test_config)

    # Check permissions are 600 (owner read/write only)
    assert oct(temp_config_file.stat().st_mode)[-3:] == "600"


def test_anthropic_command_valid_key(temp_config_dir):
    """Test anthropic command with valid API key."""
    result = runner.invoke(app, ["anthropic"], input="sk-ant-test-key\n")
    assert result.exit_code == 0
    assert "API Key saved" in result.output


def test_anthropic_command_invalid_key_warning(temp_config_dir):
    """Test anthropic command with key not starting with 'sk-'."""
    result = runner.invoke(app, ["anthropic"], input="invalid-key\n")
    assert result.exit_code == 0
    assert "Warning" in result.output
    assert "does not start with 'sk-'" in result.output


def test_anthropic_command_saves_key(temp_config_dir):
    """Test that anthropic command actually saves the key."""
    temp_config, temp_config_file = temp_config_dir
    test_key = "sk-ant-test-12345"

    result = runner.invoke(app, ["anthropic"], input=f"{test_key}\n")

    assert result.exit_code == 0
    saved_config = json.loads(temp_config_file.read_text())
    assert saved_config["anthropic_api_key"] == test_key


def test_anthropic_command_overwrites_existing_key(temp_config_dir):
    """Test that anthropic command overwrites existing key."""
    temp_config, temp_config_file = temp_config_dir
    temp_config.mkdir(parents=True, exist_ok=True)

    # Save initial key
    initial_config = {"anthropic_api_key": "sk-old-key", "other_setting": "value"}
    temp_config_file.write_text(json.dumps(initial_config))

    # Update key
    new_key = "sk-new-key"
    result = runner.invoke(app, ["anthropic"], input=f"{new_key}\n")

    assert result.exit_code == 0
    saved_config = json.loads(temp_config_file.read_text())
    assert saved_config["anthropic_api_key"] == new_key
    assert saved_config["other_setting"] == "value"  # Other settings preserved


def test_auth_help():
    """Test auth command help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Manage authentication credentials" in result.output


def test_anthropic_help():
    """Test anthropic subcommand help output."""
    result = runner.invoke(app, ["anthropic", "--help"])
    assert result.exit_code == 0
    assert "Anthropic API Key" in result.output
