"""Unit tests for the brew runner module.

These tests verify Homebrew command execution with mocked subprocess calls.
"""

from unittest.mock import patch, MagicMock

import pytest

from den.brew_runner import (
    run_brew_upgrade,
    generate_brewfile,
    BrewCommandError,
)


class TestRunBrewUpgrade:
    """Tests for run_brew_upgrade function."""

    def test_successful_upgrade(self) -> None:
        """Test successful brew upgrade execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Updated packages"
        mock_result.stderr = ""

        with patch(
            "den.brew_runner.subprocess.run", return_value=mock_result
        ) as mock_run:
            run_brew_upgrade()

            mock_run.assert_called_once_with(
                ["brew", "upgrade"],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_upgrade_failure_raises_error(self) -> None:
        """Test that failed brew upgrade raises BrewCommandError."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: some packages failed"

        with patch("den.brew_runner.subprocess.run", return_value=mock_result):
            with pytest.raises(BrewCommandError) as exc_info:
                run_brew_upgrade()

            assert exc_info.value.command == "brew upgrade"
            assert exc_info.value.returncode == 1
            assert "some packages failed" in exc_info.value.stderr

    def test_brew_not_found_raises_error(self) -> None:
        """Test that missing brew command raises BrewCommandError."""
        with patch(
            "den.brew_runner.subprocess.run",
            side_effect=FileNotFoundError("brew not found"),
        ):
            with pytest.raises(BrewCommandError) as exc_info:
                run_brew_upgrade()

            assert exc_info.value.command == "brew upgrade"
            assert exc_info.value.returncode == -1
            assert "brew command not found" in exc_info.value.stderr


class TestGenerateBrewfile:
    """Tests for generate_brewfile function."""

    def test_successful_brewfile_generation(self) -> None:
        """Test successful Brewfile generation."""
        expected_content = 'tap "homebrew/core"\nbrew "git"\ncask "firefox"'
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = expected_content
        mock_result.stderr = ""

        with patch(
            "den.brew_runner.subprocess.run", return_value=mock_result
        ) as mock_run:
            result = generate_brewfile()

            assert result == expected_content
            mock_run.assert_called_once_with(
                ["brew", "bundle", "dump", "--force", "--stdout"],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_brewfile_generation_failure_raises_error(self) -> None:
        """Test that failed brew bundle dump raises BrewCommandError."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: bundle command failed"

        with patch("den.brew_runner.subprocess.run", return_value=mock_result):
            with pytest.raises(BrewCommandError) as exc_info:
                generate_brewfile()

            assert "brew bundle dump" in exc_info.value.command
            assert exc_info.value.returncode == 1
            assert "bundle command failed" in exc_info.value.stderr

    def test_brew_not_found_raises_error(self) -> None:
        """Test that missing brew command raises BrewCommandError."""
        with patch(
            "den.brew_runner.subprocess.run",
            side_effect=FileNotFoundError("brew not found"),
        ):
            with pytest.raises(BrewCommandError) as exc_info:
                generate_brewfile()

            assert "brew bundle dump" in exc_info.value.command
            assert exc_info.value.returncode == -1
            assert "brew command not found" in exc_info.value.stderr
