"""Repository management commands.

This module provides the repo command group for creating and managing repositories.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer

from den.auth_storage import load_credentials
from den.repo_client import RepoError, create_repo, repo_exists
from den.repo_config import get_default_org

repo_app = typer.Typer(help="Repository management commands.")


@repo_app.command()
def create(
    name: str = typer.Argument(..., help="Name of the repository"),
    org: Optional[str] = typer.Option(None, "--org", help="GitHub organization name"),
) -> None:
    """Create a GitHub repository and clone it locally."""
    # Determine organization
    target_org = org or get_default_org()

    if not target_org:
        typer.echo(
            "Error: No organization configured. Please provide --org or configure repo.default_org."
        )
        raise typer.Exit(1)

    # Check local directory
    local_path = Path.home() / "Code" / name
    if local_path.exists():
        typer.echo(f"Error: Directory already exists at {local_path}")
        raise typer.Exit(1)

    # Load credentials
    credentials = load_credentials()
    github_token = credentials.get("github_token")

    if not github_token:
        typer.echo("Error: GitHub token not configured.")
        typer.echo("Run `den auth login` to configure GitHub authentication.")
        raise typer.Exit(1)

    # Check GitHub repository
    typer.echo(f"Checking repository {target_org}/{name}...")
    try:
        if repo_exists(target_org, name, github_token):
            typer.echo(
                f"Error: Repository {target_org}/{name} already exists on GitHub"
            )
            raise typer.Exit(1)
    except RepoError as e:
        typer.echo(f"Error checking repository: {e}")
        raise typer.Exit(1)

    # Create repository
    typer.echo(f"Creating repository {target_org}/{name}...")
    try:
        clone_url = create_repo(target_org, name, github_token)
    except RepoError as e:
        typer.echo(f"Error creating repository: {e}")
        raise typer.Exit(1)

    # Clone repository
    typer.echo(f"Cloning to {local_path}...")
    try:
        # Ensure parent directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            ["git", "clone", clone_url, str(local_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error cloning repository: {e.stderr}")
        raise typer.Exit(1)
    except OSError as e:
        typer.echo(f"Error executing git clone: {e}")
        raise typer.Exit(1)

    typer.echo(f"Successfully created and cloned {target_org}/{name}")
