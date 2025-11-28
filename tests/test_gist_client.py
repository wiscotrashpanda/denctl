"""Unit tests for the GitHub Gist client module.

These tests verify Gist API operations with mocked HTTP calls.
"""

from unittest.mock import patch, MagicMock

import pytest
import httpx

from den.gist_client import create_gist, update_gist, GistError


class TestCreateGist:
    """Tests for create_gist function."""

    def test_successful_gist_creation(self) -> None:
        """Test successful Gist creation returns id and url."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "abc123",
            "html_url": "https://gist.github.com/abc123",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("den.gist_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            gist_id, gist_url = create_gist("test content", "test_token")

            assert gist_id == "abc123"
            assert gist_url == "https://gist.github.com/abc123"
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args
            assert "gists" in call_kwargs[0][0]
            assert (
                call_kwargs[1]["json"]["files"]["Brewfile"]["content"] == "test content"
            )

    def test_gist_creation_http_error(self) -> None:
        """Test that HTTP errors raise GistError."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Bad credentials"
        http_error = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )
        mock_response.raise_for_status.side_effect = http_error

        with patch("den.gist_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(GistError) as exc_info:
                create_gist("test content", "bad_token")

            assert "401" in str(exc_info.value)

    def test_gist_creation_connection_error(self) -> None:
        """Test that connection errors raise GistError."""
        with patch("den.gist_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = httpx.RequestError("Connection failed")
            mock_client_class.return_value = mock_client

            with pytest.raises(GistError) as exc_info:
                create_gist("test content", "test_token")

            assert "Failed to connect" in str(exc_info.value)


class TestUpdateGist:
    """Tests for update_gist function."""

    def test_successful_gist_update(self) -> None:
        """Test successful Gist update returns url."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "abc123",
            "html_url": "https://gist.github.com/abc123",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("den.gist_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.patch.return_value = mock_response
            mock_client_class.return_value = mock_client

            gist_url = update_gist("abc123", "updated content", "test_token")

            assert gist_url == "https://gist.github.com/abc123"
            mock_client.patch.assert_called_once()
            call_kwargs = mock_client.patch.call_args
            assert "abc123" in call_kwargs[0][0]
            assert (
                call_kwargs[1]["json"]["files"]["Brewfile"]["content"]
                == "updated content"
            )

    def test_gist_update_http_error(self) -> None:
        """Test that HTTP errors raise GistError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        http_error = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        )
        mock_response.raise_for_status.side_effect = http_error

        with patch("den.gist_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.patch.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(GistError) as exc_info:
                update_gist("nonexistent", "content", "test_token")

            assert "404" in str(exc_info.value)

    def test_gist_update_connection_error(self) -> None:
        """Test that connection errors raise GistError."""
        with patch("den.gist_client.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.patch.side_effect = httpx.RequestError("Connection failed")
            mock_client_class.return_value = mock_client

            with pytest.raises(GistError) as exc_info:
                update_gist("abc123", "content", "test_token")

            assert "Failed to connect" in str(exc_info.value)
