"""Unit tests for the repo command."""

from unittest.mock import patch, MagicMock

from typer.testing import CliRunner

from den.main import app
from den.repo_client import RepoError

runner = CliRunner()


class TestRepoCreate:
    """Tests for the repo create command."""

    def test_repo_create_success_default_org(self, tmp_path):
        """Test successful creation using default organization."""
        with (
            patch("den.commands.repo.get_default_org", return_value="default-org"),
            patch(
                "den.commands.repo.load_credentials",
                return_value={"github_token": "token"},
            ),
            patch("den.commands.repo.repo_exists", return_value=False),
            patch(
                "den.commands.repo.create_repo", return_value="https://clone.url"
            ) as mock_create,
            patch("den.commands.repo.subprocess.run") as mock_run,
            patch("den.commands.repo.Path.home", return_value=tmp_path),
        ):
            result = runner.invoke(app, ["repo", "create", "my-repo"])

            assert result.exit_code == 0
            assert (
                "Successfully created and cloned default-org/my-repo" in result.output
            )
            mock_create.assert_called_with("default-org", "my-repo", "token")
            mock_run.assert_called()

    def test_repo_create_success_explicit_org(self, tmp_path):
        """Test successful creation using explicit organization."""
        with (
            patch("den.commands.repo.get_default_org", return_value="default-org"),
            patch(
                "den.commands.repo.load_credentials",
                return_value={"github_token": "token"},
            ),
            patch("den.commands.repo.repo_exists", return_value=False),
            patch(
                "den.commands.repo.create_repo", return_value="https://clone.url"
            ) as mock_create,
            patch("den.commands.repo.subprocess.run"),
            patch("den.commands.repo.Path.home", return_value=tmp_path),
        ):
            result = runner.invoke(
                app, ["repo", "create", "my-repo", "--org", "explicit-org"]
            )

            assert result.exit_code == 0
            assert (
                "Successfully created and cloned explicit-org/my-repo" in result.output
            )
            mock_create.assert_called_with("explicit-org", "my-repo", "token")

    def test_repo_create_missing_org(self, tmp_path):
        """Test error when no organization is configured or provided."""
        with (
            patch("den.commands.repo.get_default_org", return_value=None),
            patch("den.commands.repo.Path.home", return_value=tmp_path),
        ):
            result = runner.invoke(app, ["repo", "create", "my-repo"])

            assert result.exit_code == 1
            assert "Error: No organization configured" in result.output

    def test_repo_create_local_dir_exists(self, tmp_path):
        """Test error when local directory already exists."""
        # Create the directory to trigger the error
        (tmp_path / "Code" / "my-repo").mkdir(parents=True)

        with (
            patch("den.commands.repo.get_default_org", return_value="default-org"),
            patch("den.commands.repo.Path.home", return_value=tmp_path),
        ):
            result = runner.invoke(app, ["repo", "create", "my-repo"])

            assert result.exit_code == 1
            assert "Error: Directory already exists" in result.output

    def test_repo_create_missing_token(self, tmp_path):
        """Test error when GitHub token is missing."""
        with (
            patch("den.commands.repo.get_default_org", return_value="default-org"),
            patch("den.commands.repo.load_credentials", return_value={}),
            patch("den.commands.repo.Path.home", return_value=tmp_path),
        ):
            result = runner.invoke(app, ["repo", "create", "my-repo"])

            assert result.exit_code == 1
            assert "GitHub token not configured" in result.output

    def test_repo_create_repo_exists(self, tmp_path):
        """Test error when repository already exists on GitHub."""
        with (
            patch("den.commands.repo.get_default_org", return_value="default-org"),
            patch(
                "den.commands.repo.load_credentials",
                return_value={"github_token": "token"},
            ),
            patch("den.commands.repo.repo_exists", return_value=True),
            patch("den.commands.repo.Path.home", return_value=tmp_path),
        ):
            result = runner.invoke(app, ["repo", "create", "my-repo"])

            assert result.exit_code == 1
            assert "Repository default-org/my-repo already exists" in result.output

    def test_repo_create_api_error(self, tmp_path):
        """Test error handling for API failures."""
        with (
            patch("den.commands.repo.get_default_org", return_value="default-org"),
            patch(
                "den.commands.repo.load_credentials",
                return_value={"github_token": "token"},
            ),
            patch("den.commands.repo.repo_exists", side_effect=RepoError("API Error")),
            patch("den.commands.repo.Path.home", return_value=tmp_path),
        ):
            result = runner.invoke(app, ["repo", "create", "my-repo"])

            assert result.exit_code == 1
            assert "Error checking repository: API Error" in result.output
