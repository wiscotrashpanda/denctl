"""Tests for the homebrew backup module."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from anthropic import APIError
from typer.testing import CliRunner

from denctl.commands.homebrew import (
    app,
    calculate_hash,
    check_dependencies,
    format_with_claude,
    generate_brewfile,
    get_anthropic_api_key,
    get_config,
    get_general_config,
    manage_gist,
    save_config,
)

runner = CliRunner()


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Create a temporary config directory for testing."""
    temp_config = tmp_path / ".config" / "denctl"
    temp_config_file = temp_config / "homebrew.json"
    temp_general_config_file = temp_config / "config.json"

    # Patch the module-level constants
    monkeypatch.setattr("denctl.commands.homebrew.CONFIG_DIR", temp_config)
    monkeypatch.setattr("denctl.commands.homebrew.CONFIG_FILE", temp_config_file)
    monkeypatch.setattr(
        "denctl.commands.homebrew.GENERAL_CONFIG_FILE", temp_general_config_file
    )

    return temp_config, temp_config_file, temp_general_config_file


def test_get_config_no_file(temp_config_dir):
    """Test getting config when file doesn't exist."""
    config = get_config()
    assert config == {}


def test_get_config_valid_file(temp_config_dir):
    """Test getting config from valid JSON file."""
    temp_config, temp_config_file, _ = temp_config_dir
    temp_config.mkdir(parents=True, exist_ok=True)
    test_data = {"gist_id": "abc123", "last_hash": "hash123"}
    temp_config_file.write_text(json.dumps(test_data))

    config = get_config()
    assert config == test_data


def test_get_config_invalid_json(temp_config_dir):
    """Test getting config from file with invalid JSON."""
    temp_config, temp_config_file, _ = temp_config_dir
    temp_config.mkdir(parents=True, exist_ok=True)
    temp_config_file.write_text("not valid json")

    config = get_config()
    assert config == {}


def test_get_general_config_no_file(temp_config_dir):
    """Test getting general config when file doesn't exist."""
    config = get_general_config()
    assert config == {}


def test_get_general_config_valid_file(temp_config_dir):
    """Test getting general config from valid JSON file."""
    temp_config, _, temp_general_config_file = temp_config_dir
    temp_config.mkdir(parents=True, exist_ok=True)
    test_data = {"anthropic_api_key": "sk-test-key"}
    temp_general_config_file.write_text(json.dumps(test_data))

    config = get_general_config()
    assert config == test_data


def test_save_config_creates_directory(temp_config_dir):
    """Test that save_config creates directory if it doesn't exist."""
    temp_config, temp_config_file, _ = temp_config_dir
    test_config = {"gist_id": "test123"}

    save_config(test_config)

    assert temp_config.exists()
    assert temp_config_file.exists()


def test_save_config_writes_json(temp_config_dir):
    """Test that save_config writes valid JSON."""
    temp_config, temp_config_file, _ = temp_config_dir
    test_config = {"gist_id": "test123", "last_hash": "hash456"}

    save_config(test_config)

    saved_data = json.loads(temp_config_file.read_text())
    assert saved_data == test_config


def test_save_config_sets_permissions(temp_config_dir):
    """Test that save_config sets 600 permissions."""
    temp_config, temp_config_file, _ = temp_config_dir
    test_config = {"gist_id": "test123"}

    save_config(test_config)

    # Check permissions are 600 (owner read/write only)
    assert oct(temp_config_file.stat().st_mode)[-3:] == "600"


def test_calculate_hash():
    """Test SHA-256 hash calculation."""
    content = "test content"
    hash1 = calculate_hash(content)
    hash2 = calculate_hash(content)

    # Same content should produce same hash
    assert hash1 == hash2
    # Hash should be 64 characters (SHA-256 hex)
    assert len(hash1) == 64
    # Different content should produce different hash
    assert calculate_hash("different content") != hash1


def test_get_anthropic_api_key_from_env(temp_config_dir, monkeypatch):
    """Test getting API key from environment variable."""
    test_key = "sk-env-test-key"
    monkeypatch.setenv("ANTHROPIC_API_KEY", test_key)

    key = get_anthropic_api_key()
    assert key == test_key


def test_get_anthropic_api_key_from_config(temp_config_dir, monkeypatch):
    """Test getting API key from config file."""
    temp_config, _, temp_general_config_file = temp_config_dir
    temp_config.mkdir(parents=True, exist_ok=True)
    test_key = "sk-config-test-key"
    temp_general_config_file.write_text(json.dumps({"anthropic_api_key": test_key}))

    # Make sure env var is not set
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    key = get_anthropic_api_key()
    assert key == test_key


def test_get_anthropic_api_key_env_priority(temp_config_dir, monkeypatch):
    """Test that environment variable takes priority over config file."""
    temp_config, _, temp_general_config_file = temp_config_dir
    temp_config.mkdir(parents=True, exist_ok=True)

    env_key = "sk-env-key"
    config_key = "sk-config-key"

    monkeypatch.setenv("ANTHROPIC_API_KEY", env_key)
    temp_general_config_file.write_text(json.dumps({"anthropic_api_key": config_key}))

    key = get_anthropic_api_key()
    assert key == env_key


def test_get_anthropic_api_key_none(temp_config_dir, monkeypatch):
    """Test getting API key when none is configured."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    key = get_anthropic_api_key()
    assert key is None


@patch("denctl.commands.homebrew.subprocess.run")
def test_check_dependencies_success(mock_run):
    """Test dependency check when all dependencies are present."""
    # Mock successful which commands
    mock_run.side_effect = [
        Mock(returncode=0),  # which brew
        Mock(returncode=0),  # which gh
        Mock(returncode=0),  # gh auth status
    ]

    # Should not raise any exception
    check_dependencies()


@patch("denctl.commands.homebrew.subprocess.run")
def test_check_dependencies_missing_brew(mock_run):
    """Test dependency check when brew is missing."""
    mock_run.return_value = Mock(returncode=1)

    with pytest.raises(SystemExit):
        check_dependencies()


@patch("denctl.commands.homebrew.subprocess.run")
def test_check_dependencies_gh_not_authenticated(mock_run):
    """Test dependency check when gh is not authenticated."""
    mock_run.side_effect = [
        Mock(returncode=0),  # which brew
        Mock(returncode=0),  # which gh
        Mock(returncode=1),  # gh auth status fails
    ]

    with pytest.raises(SystemExit):
        check_dependencies()


@patch("denctl.commands.homebrew.subprocess.run")
def test_generate_brewfile_success(mock_run):
    """Test successful Brewfile generation."""
    expected_output = 'tap "homebrew/core"\nbrew "git"\ncask "visual-studio-code"'
    mock_run.return_value = Mock(returncode=0, stdout=expected_output)

    result = generate_brewfile()
    assert result == expected_output
    mock_run.assert_called_once()


@patch("denctl.commands.homebrew.subprocess.run")
def test_generate_brewfile_failure(mock_run):
    """Test Brewfile generation failure."""
    mock_run.side_effect = subprocess.CalledProcessError(
        1, "brew bundle dump", stderr="Error: brew not found"
    )

    with pytest.raises(SystemExit):
        generate_brewfile()


@patch("denctl.commands.homebrew.Anthropic")
def test_format_with_claude_success(mock_anthropic_class):
    """Test successful Claude formatting."""
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client

    # Mock the API response
    mock_content = Mock()
    mock_content.type = "text"
    mock_content.text = "# Formatted Brewfile\nbrew 'git'"

    mock_message = Mock()
    mock_message.content = [mock_content]

    mock_client.messages.create.return_value = mock_message

    original_content = "brew 'git'"
    result = format_with_claude(original_content, "sk-test-key")

    assert result == "# Formatted Brewfile\nbrew 'git'"
    mock_client.messages.create.assert_called_once()


@patch("denctl.commands.homebrew.Anthropic")
def test_format_with_claude_api_error(mock_anthropic_class):
    """Test Claude formatting when API error occurs."""
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client
    mock_client.messages.create.side_effect = APIError("API Error")

    original_content = "brew 'git'"
    result = format_with_claude(original_content, "sk-test-key")

    # Should return original content on error
    assert result == original_content


@patch("denctl.commands.homebrew.Anthropic")
def test_format_with_claude_exception(mock_anthropic_class):
    """Test Claude formatting when generic exception occurs."""
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("Network error")

    original_content = "brew 'git'"
    result = format_with_claude(original_content, "sk-test-key")

    # Should return original content on error
    assert result == original_content


@patch("denctl.commands.homebrew.subprocess.run")
def test_manage_gist_create_new(mock_run):
    """Test creating a new gist."""
    gist_id = "new_gist_123"
    mock_run.return_value = Mock(
        returncode=0, stdout=json.dumps({"id": gist_id}), stderr=""
    )

    config = {}
    result = manage_gist("test content", config)

    assert result == gist_id


@patch("denctl.commands.homebrew.subprocess.run")
def test_manage_gist_update_existing(mock_run):
    """Test updating an existing gist."""
    gist_id = "existing_gist_456"
    config = {"gist_id": gist_id}

    # Mock the check and update calls
    mock_run.side_effect = [
        Mock(returncode=0),  # Check if gist exists
        Mock(returncode=0),  # Update gist
    ]

    result = manage_gist("updated content", config)
    assert result == gist_id


@patch("denctl.commands.homebrew.subprocess.run")
def test_manage_gist_recreate_when_missing(mock_run):
    """Test recreating gist when previous one is missing."""
    old_gist_id = "missing_gist"
    new_gist_id = "new_gist_789"
    config = {"gist_id": old_gist_id}

    # Mock the check failing (gist not found) and create succeeding
    mock_run.side_effect = [
        Mock(returncode=1),  # Check fails - gist doesn't exist
        Mock(returncode=0, stdout=json.dumps({"id": new_gist_id})),  # Create new
    ]

    result = manage_gist("test content", config)
    assert result == new_gist_id


@patch("denctl.commands.homebrew.check_dependencies")
@patch("denctl.commands.homebrew.generate_brewfile")
@patch("denctl.commands.homebrew.get_anthropic_api_key")
@patch("denctl.commands.homebrew.manage_gist")
def test_backup_no_changes(
    mock_manage_gist, mock_get_api_key, mock_generate, mock_check_deps, temp_config_dir
):
    """Test backup when no changes detected."""
    temp_config, temp_config_file, _ = temp_config_dir

    brewfile_content = "brew 'git'"
    content_hash = calculate_hash(brewfile_content)

    # Set up existing config with same hash
    temp_config.mkdir(parents=True, exist_ok=True)
    temp_config_file.write_text(json.dumps({"last_hash": content_hash}))

    mock_generate.return_value = brewfile_content

    result = runner.invoke(app, ["backup"])

    assert result.exit_code == 0
    assert "No changes detected" in result.output
    mock_manage_gist.assert_not_called()


@patch("denctl.commands.homebrew.check_dependencies")
@patch("denctl.commands.homebrew.generate_brewfile")
@patch("denctl.commands.homebrew.get_anthropic_api_key")
@patch("denctl.commands.homebrew.manage_gist")
def test_backup_force_flag(
    mock_manage_gist, mock_get_api_key, mock_generate, mock_check_deps, temp_config_dir
):
    """Test backup with force flag ignores hash check."""
    temp_config, temp_config_file, _ = temp_config_dir

    brewfile_content = "brew 'git'"
    content_hash = calculate_hash(brewfile_content)
    gist_id = "test_gist_123"

    # Set up existing config with same hash
    temp_config.mkdir(parents=True, exist_ok=True)
    temp_config_file.write_text(json.dumps({"last_hash": content_hash}))

    mock_generate.return_value = brewfile_content
    mock_get_api_key.return_value = None  # No API key
    mock_manage_gist.return_value = gist_id

    result = runner.invoke(app, ["backup", "--force"])

    assert result.exit_code == 0
    assert "Success" in result.output
    mock_manage_gist.assert_called_once()


@patch("denctl.commands.homebrew.check_dependencies")
@patch("denctl.commands.homebrew.generate_brewfile")
@patch("denctl.commands.homebrew.get_anthropic_api_key")
def test_backup_dry_run(
    mock_get_api_key, mock_generate, mock_check_deps, temp_config_dir
):
    """Test backup with dry-run flag."""
    mock_generate.return_value = "brew 'git'\nbrew 'python'"
    mock_get_api_key.return_value = None

    result = runner.invoke(app, ["backup", "--dry-run"])

    assert result.exit_code == 0
    assert "DRY RUN" in result.output
    assert "not uploaded" in result.output


@patch("denctl.commands.homebrew.check_dependencies")
@patch("denctl.commands.homebrew.generate_brewfile")
@patch("denctl.commands.homebrew.get_anthropic_api_key")
@patch("denctl.commands.homebrew.format_with_claude")
@patch("denctl.commands.homebrew.manage_gist")
def test_backup_with_formatting(
    mock_manage_gist,
    mock_format,
    mock_get_api_key,
    mock_generate,
    mock_check_deps,
    temp_config_dir,
):
    """Test backup with Claude formatting enabled."""
    brewfile_content = "brew 'git'"
    formatted_content = "# Development Tools\nbrew 'git'  # Version control"
    gist_id = "test_gist_456"

    mock_generate.return_value = brewfile_content
    mock_get_api_key.return_value = "sk-test-key"
    mock_format.return_value = formatted_content
    mock_manage_gist.return_value = gist_id

    result = runner.invoke(app, ["backup"])

    assert result.exit_code == 0
    assert "Success" in result.output
    mock_format.assert_called_once_with(brewfile_content, "sk-test-key")
    mock_manage_gist.assert_called_once_with(formatted_content, {})


@patch("denctl.commands.homebrew.check_dependencies")
@patch("denctl.commands.homebrew.generate_brewfile")
@patch("denctl.commands.homebrew.get_anthropic_api_key")
@patch("denctl.commands.homebrew.manage_gist")
def test_backup_no_format_flag(
    mock_manage_gist, mock_get_api_key, mock_generate, mock_check_deps, temp_config_dir
):
    """Test backup with --no-format flag."""
    brewfile_content = "brew 'git'"
    gist_id = "test_gist_789"

    mock_generate.return_value = brewfile_content
    mock_get_api_key.return_value = "sk-test-key"
    mock_manage_gist.return_value = gist_id

    result = runner.invoke(app, ["backup", "--no-format"])

    assert result.exit_code == 0
    # Should upload raw content without formatting
    mock_manage_gist.assert_called_once_with(brewfile_content, {})


def test_homebrew_help():
    """Test homebrew command help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Manage Homebrew backups" in result.output


def test_backup_help():
    """Test backup subcommand help output."""
    result = runner.invoke(app, ["backup", "--help"])
    assert result.exit_code == 0
    assert "--force" in result.output
    assert "--dry-run" in result.output
    assert "--no-format" in result.output
