"""Tests for the main application entry point."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from den.main import app, main, version_callback

runner = CliRunner()


def test_app_no_args_shows_help():
    """Test that running with no args shows help due to no_args_is_help=True."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "den - 🦝 automation CLI" in result.output
    assert "hello" in result.output
    assert "homebrew" in result.output
    assert "auth" in result.output


def test_app_help_flag():
    """Test main app help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "den - 🦝 automation CLI" in result.output
    assert "Usage:" in result.output


def test_app_version_flag():
    """Test version flag displays version."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "den version:" in result.output


def test_app_version_short_flag():
    """Test short version flag -v."""
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    assert "den version:" in result.output


def test_version_callback_exits():
    """Test that version_callback raises Exit when value is True."""
    with pytest.raises(SystemExit):
        version_callback(True)


def test_version_callback_no_exit_on_false():
    """Test that version_callback does nothing when value is False."""
    # Should not raise
    version_callback(False)


def test_hello_command_registered():
    """Test that hello command is properly registered."""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello World!" in result.output


def test_hello_command_with_arg():
    """Test hello command with custom name."""
    result = runner.invoke(app, ["hello", "Test"])
    assert result.exit_code == 0
    assert "Hello Test!" in result.output


def test_homebrew_command_group_registered():
    """Test that homebrew command group is registered."""
    result = runner.invoke(app, ["homebrew", "--help"])
    assert result.exit_code == 0
    assert "Manage Homebrew backups" in result.output
    assert "backup" in result.output


def test_auth_command_group_registered():
    """Test that auth command group is registered."""
    result = runner.invoke(app, ["auth", "--help"])
    assert result.exit_code == 0
    assert "Manage authentication credentials" in result.output
    assert "anthropic" in result.output


def test_invalid_command():
    """Test that invalid command shows error."""
    result = runner.invoke(app, ["nonexistent"])
    assert result.exit_code != 0
    assert "No such command" in result.output or "Error" in result.output


@patch("den.main.app")
def test_main_function_calls_app(mock_app):
    """Test that main() function calls the app."""
    main()
    mock_app.assert_called_once()


def test_all_commands_have_help():
    """Test that all main commands have help text."""
    # Test hello
    result = runner.invoke(app, ["hello", "--help"])
    assert result.exit_code == 0
    assert "Say hello" in result.output or "NAME" in result.output

    # Test homebrew
    result = runner.invoke(app, ["homebrew", "--help"])
    assert result.exit_code == 0
    assert "backup" in result.output

    # Test auth
    result = runner.invoke(app, ["auth", "--help"])
    assert result.exit_code == 0
    assert "anthropic" in result.output


def test_version_in_help():
    """Test that version option is shown in main help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--version" in result.output or "-v" in result.output


def test_command_context_preserved():
    """Test that typer context is properly initialized."""
    # This ensures the common callback doesn't break command execution
    result = runner.invoke(app, ["hello", "Context"])
    assert result.exit_code == 0
    assert "Hello Context!" in result.output


def test_multiple_commands_isolation():
    """Test that running multiple commands maintains isolation."""
    result1 = runner.invoke(app, ["hello", "First"])
    result2 = runner.invoke(app, ["hello", "Second"])

    assert result1.exit_code == 0
    assert "Hello First!" in result1.output

    assert result2.exit_code == 0
    assert "Hello Second!" in result2.output


def test_app_name():
    """Test that app name is correctly set."""
    # The app name should appear in help output
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "den" in result.output.lower()
