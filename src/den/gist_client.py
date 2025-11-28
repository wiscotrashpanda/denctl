"""GitHub Gist API client functions.

This module handles creating and updating GitHub Gists using the GitHub API.
"""

import httpx

GITHUB_API_BASE = "https://api.github.com"


class GistError(Exception):
    """Exception raised for Gist API errors."""

    pass


def create_gist(
    content: str, token: str, description: str = "Brewfile backup"
) -> tuple[str, str]:
    """Create a new GitHub Gist.

    Args:
        content: The content to store in the Gist.
        token: GitHub personal access token.
        description: Description for the Gist.

    Returns:
        Tuple of (gist_id, gist_url).

    Raises:
        GistError: If the API call fails.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {
        "description": description,
        "public": False,
        "files": {
            "Brewfile": {
                "content": content,
            }
        },
    }

    try:
        with httpx.Client() as client:
            response = client.post(
                f"{GITHUB_API_BASE}/gists",
                headers=headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["id"], data["html_url"]
    except httpx.HTTPStatusError as e:
        raise GistError(
            f"Failed to create Gist: {e.response.status_code} - {e.response.text}"
        ) from e
    except httpx.RequestError as e:
        raise GistError(f"Failed to connect to GitHub API: {e}") from e


def update_gist(gist_id: str, content: str, token: str) -> str:
    """Update an existing GitHub Gist.

    Args:
        gist_id: The ID of the Gist to update.
        content: The new content for the Gist.
        token: GitHub personal access token.

    Returns:
        The Gist URL.

    Raises:
        GistError: If the API call fails.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {
        "files": {
            "Brewfile": {
                "content": content,
            }
        },
    }

    try:
        with httpx.Client() as client:
            response = client.patch(
                f"{GITHUB_API_BASE}/gists/{gist_id}",
                headers=headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["html_url"]
    except httpx.HTTPStatusError as e:
        raise GistError(
            f"Failed to update Gist: {e.response.status_code} - {e.response.text}"
        ) from e
    except httpx.RequestError as e:
        raise GistError(f"Failed to connect to GitHub API: {e}") from e
