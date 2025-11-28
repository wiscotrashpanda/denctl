"""Integration tests for the brew upgrade command.

Tests for the full workflow with mocked external services.
"""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from den.main import app

runner = CliRunner()


class TestBrewUpgradeCommand:
    """Tests for the brew upgrade command."""

    @patch("den.commands.brew.run_brew_upgrade")
    @patch("den.commands.brew.generate_brewfile")
    @patch("den.commands.brew.load_credentials")
    @patch("den.commands.brew.format_brewfile")
    @patch("den.commands.brew.create_gist")
    @patch("den.commands.brew.get_brew_state")
    @patch("den.commands.brew.save_brew_state")
    @patch("den.commands.brew.setup_brew_logger")
    def test_full_workflow_creates_new_gist(
        self,
        mock_logger: MagicMock,
        mock_save_state: MagicMock,
        mock_get_state: MagicMock,
        mock_create_gist: MagicMock,
        mock_format: MagicMock,
        mock_credentials: MagicMock,
        mock_generate: MagicMock,
        mock_upgrade: MagicMock,
    ) -> None:
        """Test full workflow with mocked external services.

        _Requirements: 1.2, 2.4, 3.6, 4.6_
        """
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_get_state.return_value = None  # No existing state
        mock_generate.return_value = "tap 'homebrew/core'\nbrew 'git'"
        mock_credentials.return_value = {
            "anthropic_api_key": "test-anthropic-key",
            "github_token": "test-github-token",
        }
        mock_format.return_value = "# Formatted Brewfile\nbrew 'git'"
        mock_create_gist.return_value = ("gist123", "https://gist.github.com/gist123")

        result = runner.invoke(app, ["brew", "upgrade"])

        assert result.exit_code == 0
        assert "Updating Homebrew dependencies..." in result.output
        assert "Creating Brewfile..." in result.output
        assert "Formatting Brewfile with AI..." in result.output
        assert "Backing up Brewfile to GitHub Gist..." in result.output
        assert "https://gist.github.com/gist123" in result.output
        mock_save_state.assert_called_once()

    @patch("den.commands.brew.run_brew_upgrade")
    @patch("den.commands.brew.generate_brewfile")
    @patch("den.commands.brew.load_credentials")
    @patch("den.commands.brew.format_brewfile")
    @patch("den.commands.brew.update_gist")
    @patch("den.commands.brew.get_brew_state")
    @patch("den.commands.brew.save_brew_state")
    @patch("den.commands.brew.setup_brew_logger")
    def test_full_workflow_updates_existing_gist(
        self,
        mock_logger: MagicMock,
        mock_save_state: MagicMock,
        mock_get_state: MagicMock,
        mock_update_gist: MagicMock,
        mock_format: MagicMock,
        mock_credentials: MagicMock,
        mock_generate: MagicMock,
        mock_upgrade: MagicMock,
    ) -> None:
        """Test workflow updates existing Gist when gist_id exists.

        _Requirements: 1.2, 4.6_
        """
        mock_logger.return_value = MagicMock()
        mock_get_state.return_value = {
            "brewfile_hash": "sha256:oldhash",
            "gist_id": "existing-gist-id",
        }
        mock_generate.return_value = "tap 'homebrew/core'\nbrew 'git'\nbrew 'vim'"
        mock_credentials.return_value = {
            "anthropic_api_key": "test-anthropic-key",
            "github_token": "test-github-token",
        }
        mock_format.return_value = "# Formatted Brewfile\nbrew 'git'\nbrew 'vim'"
        mock_update_gist.return_value = "https://gist.github.com/existing-gist-id"

        result = runner.invoke(app, ["brew", "upgrade"])

        assert result.exit_code == 0
        assert "https://gist.github.com/existing-gist-id" in result.output
        mock_update_gist.assert_called_once()

    @patch("den.commands.brew.run_brew_upgrade")
    @patch("den.commands.brew.generate_brewfile")
    @patch("den.commands.brew.get_brew_state")
    @patch("den.commands.brew.setup_brew_logger")
    def test_skip_when_brewfile_unchanged(
        self,
        mock_logger: MagicMock,
        mock_get_state: MagicMock,
        mock_generate: MagicMock,
        mock_upgrade: MagicMock,
    ) -> None:
        """Test skip behavior when Brewfile unchanged.

        _Requirements: 2.4_
        """
        mock_logger.return_value = MagicMock()
        brewfile_content = "tap 'homebrew/core'\nbrew 'git'"
        mock_generate.return_value = brewfile_content

        # Compute the expected hash
        from den.hash_utils import compute_hash

        expected_hash = compute_hash(brewfile_content)

        mock_get_state.return_value = {
            "brewfile_hash": expected_hash,
            "gist_id": "existing-gist-id",
        }

        result = runner.invoke(app, ["brew", "upgrade"])

        assert result.exit_code == 0
        assert "Brewfile unchanged, skipping backup" in result.output

    @patch("den.commands.brew.run_brew_upgrade")
    @patch("den.commands.brew.generate_brewfile")
    @patch("den.commands.brew.load_credentials")
    @patch("den.commands.brew.get_brew_state")
    @patch("den.commands.brew.setup_brew_logger")
    def test_error_missing_anthropic_key(
        self,
        mock_logger: MagicMock,
        mock_get_state: MagicMock,
        mock_credentials: MagicMock,
        mock_generate: MagicMock,
        mock_upgrade: MagicMock,
    ) -> None:
        """Test error handling for missing Anthropic credentials.

        _Requirements: 3.6_
        """
        mock_logger.return_value = MagicMock()
        mock_get_state.return_value = None
        mock_generate.return_value = "brew 'git'"
        mock_credentials.return_value = {"github_token": "test-token"}

        result = runner.invoke(app, ["brew", "upgrade"])

        assert result.exit_code == 1
        assert "Anthropic API key not configured" in result.output
        assert "den auth login" in result.output

    @patch("den.commands.brew.run_brew_upgrade")
    @patch("den.commands.brew.generate_brewfile")
    @patch("den.commands.brew.load_credentials")
    @patch("den.commands.brew.get_brew_state")
    @patch("den.commands.brew.setup_brew_logger")
    def test_error_missing_github_token(
        self,
        mock_logger: MagicMock,
        mock_get_state: MagicMock,
        mock_credentials: MagicMock,
        mock_generate: MagicMock,
        mock_upgrade: MagicMock,
    ) -> None:
        """Test error handling for missing GitHub credentials.

        _Requirements: 4.6_
        """
        mock_logger.return_value = MagicMock()
        mock_get_state.return_value = None
        mock_generate.return_value = "brew 'git'"
        mock_credentials.return_value = {"anthropic_api_key": "test-key"}

        result = runner.invoke(app, ["brew", "upgrade"])

        assert result.exit_code == 1
        assert "GitHub token not configured" in result.output
        assert "den auth login" in result.output
