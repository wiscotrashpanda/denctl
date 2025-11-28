"""Brew commands for Homebrew management.

This module provides the brew command group for managing Homebrew packages,
including the upgrade command that updates packages and backs up the Brewfile.
"""

import typer

from den.auth_storage import load_credentials
from den.brew_logger import setup_brew_logger
from den.brew_runner import BrewCommandError, generate_brewfile, run_brew_upgrade
from den.brewfile_formatter import BrewfileFormatterError, format_brewfile
from den.gist_client import GistError, create_gist, update_gist
from den.hash_utils import compute_hash
from den.state_storage import get_brew_state, save_brew_state

brew_app = typer.Typer(help="Homebrew management commands.")


@brew_app.command()
def upgrade(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force backup even if Brewfile unchanged"
    ),
) -> None:
    """Upgrade Homebrew packages and backup Brewfile to GitHub Gist."""
    logger = setup_brew_logger()
    logger.info("Starting brew upgrade process")

    # Step 1: Run brew upgrade
    typer.echo("Updating Homebrew dependencies...")
    logger.info("Updating Homebrew dependencies...")
    try:
        run_brew_upgrade()
        logger.info("brew upgrade completed successfully")
    except BrewCommandError as e:
        logger.error(f"brew upgrade failed: {e}")
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

    # Step 2: Generate Brewfile
    typer.echo("Creating Brewfile...")
    logger.info("Creating Brewfile...")
    try:
        brewfile_content = generate_brewfile()
        logger.info("Brewfile generated successfully")
    except BrewCommandError as e:
        logger.error(f"Failed to generate Brewfile: {e}")
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

    # Step 3: Compute hash and check for changes
    new_hash = compute_hash(brewfile_content)
    logger.info(f"Computed Brewfile hash: {new_hash}")

    brew_state = get_brew_state()
    existing_hash = brew_state.get("brewfile_hash") if brew_state else None
    existing_gist_id = brew_state.get("gist_id") if brew_state else None

    if existing_hash == new_hash and not force:
        typer.echo("Brewfile unchanged, skipping backup")
        logger.info("Brewfile unchanged, skipping backup")
        return

    if force and existing_hash == new_hash:
        logger.info("Force flag set, proceeding despite unchanged Brewfile")

    # Step 4: Load credentials
    credentials = load_credentials()
    anthropic_key = credentials.get("anthropic_api_key")
    github_token = credentials.get("github_token")

    if not anthropic_key:
        logger.error("Anthropic API key not configured")
        typer.echo("Error: Anthropic API key not configured.")
        typer.echo("Run `den auth login` to configure Anthropic credentials.")
        raise typer.Exit(1)

    if not github_token:
        logger.error("GitHub token not configured")
        typer.echo("Error: GitHub token not configured.")
        typer.echo("Run `den auth login` to configure GitHub authentication.")
        raise typer.Exit(1)

    # Step 5: Format Brewfile with Anthropic
    typer.echo("Formatting Brewfile with AI...")
    logger.info("Formatting Brewfile with AI...")
    try:
        formatted_content = format_brewfile(brewfile_content, anthropic_key)
        logger.info("Brewfile formatted successfully")
    except BrewfileFormatterError as e:
        logger.error(f"Failed to format Brewfile: {e}")
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

    # Step 6: Backup to GitHub Gist
    typer.echo("Backing up Brewfile to GitHub Gist...")
    logger.info("Backing up Brewfile to GitHub Gist...")
    try:
        if existing_gist_id:
            gist_url = update_gist(existing_gist_id, formatted_content, github_token)
            gist_id = existing_gist_id
            logger.info(f"Updated existing Gist: {gist_url}")
        else:
            gist_id, gist_url = create_gist(formatted_content, github_token)
            logger.info(f"Created new Gist: {gist_url}")
    except GistError as e:
        logger.error(f"Failed to backup to Gist: {e}")
        typer.echo(f"Error: {e}")
        raise typer.Exit(1)

    # Step 7: Save state
    try:
        save_brew_state(new_hash, gist_id)
        logger.info(f"Saved brew state: hash={new_hash}, gist_id={gist_id}")
    except OSError as e:
        logger.error(f"Failed to save state: {e}")
        typer.echo(f"Error: Failed to save state - {e}")
        raise typer.Exit(1)

    # Step 8: Display success message
    typer.echo(f"Brewfile backed up successfully: {gist_url}")
    logger.info("Brew upgrade process completed successfully")
