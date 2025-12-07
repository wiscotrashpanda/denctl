"""Unit tests for the GitHub Repository client module.

These tests verify Repo API operations with mocked HTTP calls.
"""

from unittest.mock import patch, MagicMock

import pytest
import httpx

from den.repo_client import create_repo, repo_exists, RepoError


class TestRepoExists:
    """Tests for repo_exists function."""

    def test_repo_exists_returns_true(self) -> None:
        """Test repo_exists returns True when API returns 200."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("den.repo_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            exists = repo_exists("my-org", "my-repo", "test_token")

            assert exists is True
            mock_client.get.assert_called_once()
            call_kwargs = mock_client.get.call_args
            assert "repos/my-org/my-repo" in call_kwargs[0][0]

    def test_repo_exists_returns_false_on_404(self) -> None:
        """Test repo_exists returns False when API returns 404."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("den.repo_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            exists = repo_exists("my-org", "my-repo", "test_token")

            assert exists is False

    def test_repo_exists_http_error(self) -> None:
        """Test that HTTP errors (other than 404) raise RepoError."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Bad credentials"
        http_error = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )
        mock_response.raise_for_status.side_effect = http_error

        with patch("den.repo_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(RepoError) as exc_info:
                repo_exists("my-org", "my-repo", "test_token")

            assert "401" in str(exc_info.value)

    def test_repo_exists_connection_error(self) -> None:
        """Test that connection errors raise RepoError."""
        with patch("den.repo_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = httpx.RequestError("Connection failed")
            mock_client_class.return_value = mock_client

            with pytest.raises(RepoError) as exc_info:
                repo_exists("my-org", "my-repo", "test_token")

            assert "Failed to connect" in str(exc_info.value)


class TestCreateRepo:
    """Tests for create_repo function."""

    def test_successful_repo_creation(self) -> None:
        """Test successful repo creation returns clone url."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "clone_url": "https://github.com/my-org/my-repo.git",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("den.repo_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            clone_url = create_repo("my-org", "my-repo", "test_token")

            assert clone_url == "https://github.com/my-org/my-repo.git"
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args
            assert "orgs/my-org/repos" in call_kwargs[0][0]
            assert call_kwargs[1]["json"]["name"] == "my-repo"
            assert call_kwargs[1]["json"]["private"] is False

    def test_repo_creation_http_error(self) -> None:
        """Test that HTTP errors raise RepoError."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = "Repository already exists"
        http_error = httpx.HTTPStatusError(
            "Unprocessable Entity", request=MagicMock(), response=mock_response
        )
        mock_response.raise_for_status.side_effect = http_error

        with patch("den.repo_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(RepoError) as exc_info:
                create_repo("my-org", "my-repo", "test_token")

            assert "422" in str(exc_info.value)

    def test_repo_creation_connection_error(self) -> None:
        """Test that connection errors raise RepoError."""
        with patch("den.repo_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = httpx.RequestError("Connection failed")
            mock_client_class.return_value = mock_client

            with pytest.raises(RepoError) as exc_info:
                create_repo("my-org", "my-repo", "test_token")

            assert "Failed to connect" in str(exc_info.value)
