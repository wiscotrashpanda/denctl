"""GitHub Repository API client functions.

This module handles creating and checking GitHub repositories using the GitHub API.
"""

import httpx

GITHUB_API_BASE = "https://api.github.com"


class RepoError(Exception):
    """Exception raised for Repo API errors."""

    pass


def repo_exists(org: str, name: str, token: str) -> bool:
    """Check if a GitHub repository exists.

    Args:
      org: The organization name.
      name: The repository name.
      token: GitHub personal access token.

    Returns:
      True if the repository exists, False otherwise.

    Raises:
      RepoError: If the API call fails (network error, auth error, etc).
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        with httpx.Client() as client:
            response = client.get(
                f"{GITHUB_API_BASE}/repos/{org}/{name}",
                headers=headers,
                timeout=30.0,
            )
            if response.status_code == 200:
                return True
            if response.status_code == 404:
                return False
            response.raise_for_status()
            return False  # Should be unreachable due to raise_for_status
    except httpx.HTTPStatusError as e:
        raise RepoError(
            f"Failed to check repository existence: {e.response.status_code} - {e.response.text}"
        ) from e
    except httpx.RequestError as e:
        raise RepoError(f"Failed to connect to GitHub API: {e}") from e


def create_repo(org: str, name: str, token: str) -> str:
    """Create a new GitHub repository in an organization.

    Args:
      org: The organization name.
      name: The repository name.
      token: GitHub personal access token.

    Returns:
      The clone URL of the created repository.

    Raises:
      RepoError: If the API call fails.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {
        "name": name,
        "private": False,  # Default to public as per spec
    }

    try:
        with httpx.Client() as client:
            response = client.post(
                f"{GITHUB_API_BASE}/orgs/{org}/repos",
                headers=headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["clone_url"]
    except httpx.HTTPStatusError as e:
        raise RepoError(
            f"Failed to create repository: {e.response.status_code} - {e.response.text}"
        ) from e
    except httpx.RequestError as e:
        raise RepoError(f"Failed to connect to GitHub API: {e}") from e
