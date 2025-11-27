"""
Homebrew Backup and Management Module.

This module implements the `den homebrew` command group, which currently handles
the automated backup of the local Homebrew configuration to a GitHub Gist.

Key Features:
- **Brewfile Generation**: Dumps the current Homebrew state (taps, brews, casks).
- **Change Detection**: Uses SHA-256 hashing to prevent unnecessary uploads if the configuration hasn't changed.
- **AI Formatting**: Uses the Anthropic API (Claude) to organize and comment the Brewfile for better readability.
- **Gist Integration**: Automatically creates or updates a private GitHub Gist with the backup.
- **State Management**: Persists the Gist ID and content hash to track state across runs.

Configuration:
- Stores state (Gist ID, Hash) in `~/.config/den/homebrew.json`.
- Reads API keys from `~/.config/den/config.json` or environment variables.
"""

import hashlib
import json
import os
import plistlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from anthropic import Anthropic, APIError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Initialize the homebrew sub-application
app = typer.Typer(name="homebrew", help="Manage Homebrew backups and configuration.")
schedule_app = typer.Typer(name="schedule", help="Manage automated backup schedule.")
app.add_typer(schedule_app, name="schedule")

console = Console()

# Configuration Constants
CONFIG_DIR = Path.home() / ".config" / "den"
CONFIG_FILE = CONFIG_DIR / "homebrew.json"
GENERAL_CONFIG_FILE = CONFIG_DIR / "config.json"

# Scheduling Constants
PLIST_LABEL = "com.emkaytec.den.homebrew.plist"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / PLIST_LABEL


def get_config() -> Dict[str, Any]:
    """
    Load the Homebrew-specific configuration from the JSON file.

    This file stores state information like the last backup hash,
    the Gist ID, and the last run timestamp.

    Returns:
        Dict[str, Any]: The configuration dictionary. Returns empty dict on error.
    """
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def get_general_config() -> Dict[str, Any]:
    """
    Load the general application configuration.

    This file is used to retrieve shared secrets, specifically the
    Anthropic API key.

    Returns:
        Dict[str, Any]: The configuration dictionary. Returns empty dict on error.
    """
    if not GENERAL_CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(GENERAL_CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """
    Save the Homebrew-specific configuration to the JSON file.

    Ensures directory exists and sets 600 permissions for security.

    Args:
        config (Dict[str, Any]): The configuration data to save.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    # Ensure privacy
    CONFIG_FILE.chmod(0o600)


def check_dependencies():
    """
    Verify that required external tools are installed and configured.

    Checks for:
    1. `brew`: The Homebrew package manager itself.
    2. `gh`: The GitHub CLI tool.
    3. GitHub Authentication: Verifies `gh` is logged in.

    Raises:
        typer.Exit: If any dependency is missing or not authenticated.
    """
    for cmd in ["brew", "gh"]:
        if subprocess.run(["which", cmd], capture_output=True).returncode != 0:
            console.print(
                f"[bold red]Error:[/bold red] '{cmd}' is not installed or not in PATH."
            )
            raise typer.Exit(code=1)

    # Check if gh is authenticated
    if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
        console.print(
            "[bold red]Error:[/bold red] GitHub CLI is not authenticated. Run 'gh auth login'."
        )
        raise typer.Exit(code=1)


def generate_brewfile() -> str:
    """
    Generate the Brewfile content using `brew bundle dump`.

    This runs the external brew command and captures its stdout.
    The `--file=-` flag tells brew to dump to stdout instead of a file.

    Returns:
        str: The raw content of the Brewfile.

    Raises:
        typer.Exit: If the brew command fails.
    """
    try:
        result = subprocess.run(
            ["brew", "bundle", "dump", "--file=-"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        console.print(
            f"[bold red]Error running brew bundle dump:[/bold red] {e.stderr}"
        )
        raise typer.Exit(code=2) from e


def calculate_hash(content: str) -> str:
    """
    Calculate a SHA-256 hash of the provided content.

    This is used for change detection to avoid unnecessary API calls and commits.

    Args:
        content (str): The string content to hash.

    Returns:
        str: The hexadecimal representation of the hash.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_anthropic_api_key() -> Optional[str]:
    """
    Retrieve Anthropic API key from Environment or General Configuration.

    Priority:
    1. Environment Variable (`ANTHROPIC_API_KEY`)
    2. Config File (`~/.config/den/config.json`)

    Returns:
        Optional[str]: The API key if found, else None.
    """
    # 1. Environment Variable
    env_key = os.environ.get("ANTHROPIC_API_KEY")
    if env_key:
        return env_key

    # 2. General Config File
    config = get_general_config()
    config_key = config.get("anthropic_api_key")
    if config_key:
        return config_key

    return None


def format_with_claude(content: str, api_key: str) -> str:
    """
    Use the Anthropic API (Claude) to format and document the Brewfile.

    This sends the raw Brewfile to Claude with instructions to:
    - Add headers.
    - Categorize packages (Dev tools, Utilities, etc.).
    - Add comments explaining what packages do.
    - STRICTLY preserve package names and syntax.

    Args:
        content (str): The raw Brewfile content.
        api_key (str): The Anthropic API key.

    Returns:
        str: The formatted Brewfile content, or the original content if the API call fails.
    """
    client = Anthropic(api_key=api_key)

    system_prompt = (
        "You are a technical documentation expert. "
        "Format and document this Homebrew Brewfile.\n\n"
        "Instructions:\n"
        "1. Add a clear header explaining what this Brewfile is\n"
        "2. Group packages into logical categories with headers "
        "(e.g., # Development Tools, # System Utilities, # Productivity Apps, "
        "# Media & Entertainment, # Design & Creative)\n"
        "3. Add brief inline comments explaining what each package/cask does\n"
        "4. Keep the exact package names, tap names, and syntax UNCHANGED\n"
        "5. Maintain all taps, mas (Mac App Store), and vscode entries "
        "exactly as they appear\n"
        "6. Return ONLY the formatted Brewfile content with no additional explanations "
        "or markdown code blocks"
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": content}],
        )

        if (
            message.content
            and len(message.content) > 0
            and message.content[0].type == "text"
        ):
            return message.content[0].text
        return content

    except APIError as e:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] Claude API error: {e}. "
            "Using unformatted content."
        )
        return content
    except Exception as e:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] Formatting failed: {e}. "
            "Using unformatted content."
        )
        return content


def manage_gist(content: str, config: Dict[str, Any]) -> str:
    """
    Create or update a GitHub Gist with the backup content.

    Logic:
    1. Checks if a Gist ID is stored in the config.
    2. If yes, verify it exists via API.
    3. If it exists, UPDATE it (PATCH).
    4. If it doesn't exist (or config is empty), CREATE a new one (POST).

    Args:
        content (str): The file content to upload.
        config (Dict[str, Any]): The current configuration state.

    Returns:
        str: The ID of the created or updated Gist.

    Raises:
        typer.Exit: If the GitHub CLI command fails.
    """
    gist_id = config.get("gist_id")
    description = "Homebrew Backup"
    filename = "Brewfile"

    # Check if Gist exists
    gist_exists = False
    if gist_id:
        check_proc = subprocess.run(
            ["gh", "api", f"/gists/{gist_id}"], capture_output=True
        )
        if check_proc.returncode == 0:
            gist_exists = True
        else:
            console.print(
                f"[yellow]Previous Gist {gist_id} not found. Creating new one.[/yellow]"
            )
            gist_id = None  # Reset to create new

    if gist_exists and gist_id:
        # Update existing Gist
        payload = {
            "description": description,
            "files": {filename: {"content": content}},
        }

        try:
            subprocess.run(
                ["gh", "api", f"/gists/{gist_id}", "-X", "PATCH", "--input", "-"],
                input=json.dumps(payload),
                check=True,
                capture_output=True,
                text=True,
            )
            return gist_id
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]Error updating Gist:[/bold red] {e.stderr}")
            raise typer.Exit(code=3) from e

    else:
        # Create new Gist
        payload = {
            "description": description,
            "public": False,
            "files": {filename: {"content": content}},
        }

        try:
            result = subprocess.run(
                ["gh", "api", "/gists", "-X", "POST", "--input", "-"],
                input=json.dumps(payload),
                check=True,
                capture_output=True,
                text=True,
            )
            response_data = json.loads(result.stdout)
            return response_data["id"]
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]Error creating Gist:[/bold red] {e.stderr}")
            raise typer.Exit(code=3) from e


@app.command()
def backup(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force backup even if no changes detected."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Generate and format but do not upload."
    ),
    no_format: bool = typer.Option(False, "--no-format", help="Skip AI formatting."),
):
    """
    Backup Homebrew configuration to GitHub Gist with optional AI formatting.

    Workflow:
    1. Verify dependencies (brew, gh).
    2. Generate Brewfile (`brew bundle dump`).
    3. Calculate Hash and compare with previous run (Change Detection).
    4. If changed (or forced):
       a. Format content using Claude (optional).
       b. Upload to GitHub Gist.
       c. Update state configuration.
    """
    check_dependencies()
    config = get_config()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        # Step 1: Generate Brewfile
        progress.add_task(description="Generating Brewfile...", total=None)
        raw_content = generate_brewfile()
        current_hash = calculate_hash(raw_content)

        # Step 2: Check for changes
        last_hash = config.get("last_hash")

        if not force and last_hash == current_hash:
            console.print(
                "[green]✓[/green] No changes detected in Homebrew configuration."
            )
            return

        final_content = raw_content

        # Step 3: Format with Claude
        api_key = get_anthropic_api_key()
        if not no_format and api_key:
            progress.add_task(description="Formatting with Claude AI...", total=None)
            final_content = format_with_claude(raw_content, api_key)
        elif not no_format and not api_key:
            console.print(
                "[yellow]Warning:[/yellow] ANTHROPIC_API_KEY not found. "
                "Run 'den auth anthropic' or set env var. Skipping formatting."
            )

        # Step 4: Upload
        if dry_run:
            console.print(
                "[bold blue]DRY RUN:[/bold blue] content generated but not uploaded."
            )
            console.print(f"Hash: {current_hash}")
            console.print(f"Content Length: {len(final_content)} chars")
            # Optionally print head of content
            console.print("--- Preview (first 10 lines) ---")
            console.print("\n".join(final_content.splitlines()[:10]))
            return

        progress.add_task(description="Uploading to GitHub Gist...", total=None)
        gist_id = manage_gist(final_content, config)

        # Step 5: Update Config
        config.update(
            {
                "gist_id": gist_id,
                "last_hash": current_hash,
                "last_run_timestamp": datetime.now(timezone.utc).isoformat(),
                "gist_url": f"https://gist.github.com/{gist_id}",
            }
        )
        save_config(config)

    console.print(
        f"[bold green]Success![/bold green] Backup complete. Gist ID: {gist_id}"
    )


@schedule_app.command("install")
def schedule_install():
    """
    Install the launchd agent to run 'den homebrew backup' daily at 06:00 UTC.

    This command:
    1. Calculates the local time corresponding to 06:00 UTC.
    2. Generates a launchd plist file.
    3. Loads the agent using launchctl.
    """
    # Calculate local time for 06:00 UTC
    # TODO: Add CLI option to specify custom schedule time (default: 06:00 UTC)
    utc_target = datetime.now(timezone.utc).replace(
        hour=6, minute=0, second=0, microsecond=0
    )
    local_target = utc_target.astimezone()

    console.print(
        f"Scheduling backup for 06:00 UTC (approx. {local_target.strftime('%H:%M')} local time)."
    )

    # Determine the executable path
    # We use sys.executable to find the python interpreter, but we want the 'den' script
    # equivalent if possible, or run module.
    # However, 'den' is likely an entry point script.
    # Safest way in a 'uv' or 'venv' environment is to use the absolute path to the executable script.
    executable = sys.argv[0]
    if not os.path.isabs(executable):
        executable = os.path.abspath(executable)

    # If run via 'uv run', sys.argv[0] might be different.
    # But typically sys.argv[0] is the script path.
    # Let's verify if it's python or the script.
    # If it ends in 'den', we are good. If it is 'python', we need the module args.
    # A robust way for a CLI installed via pip/uv is to assume 'den' is on the path or use the full path.

    # Let's construct the command arguments
    program_args = [executable, "homebrew", "backup"]

    plist_content = {
        "Label": PLIST_LABEL,
        "ProgramArguments": program_args,
        "StartCalendarInterval": {
            "Hour": local_target.hour,
            "Minute": local_target.minute,
        },
        "StandardOutPath": str(Path.home() / "Library/Logs/den.homebrew.log"),
        "StandardErrorPath": str(Path.home() / "Library/Logs/den.homebrew.error.log"),
        "RunAtLoad": False,
    }

    try:
        PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PLIST_PATH, "wb") as f:
            plistlib.dump(plist_content, f)

        console.print(f"[green]✓[/green] Created plist at {PLIST_PATH}")

        # Unload if exists first to ensure clean reload
        subprocess.run(
            ["launchctl", "bootout", f"gui/{os.getuid()}/{PLIST_LABEL}"],
            capture_output=True,
        )

        # Load the agent
        # launchctl bootstrap gui/<uid> <path>
        result = subprocess.run(
            ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(PLIST_PATH)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            console.print("[bold green]Success![/bold green] Backup scheduled.")
        else:
            console.print(f"[bold red]Error loading agent:[/bold red] {result.stderr}")
            # Cleanup if failed
            if PLIST_PATH.exists():
                PLIST_PATH.unlink()
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[bold red]Error installing schedule:[/bold red] {e}")
        raise typer.Exit(code=1)


@schedule_app.command("uninstall")
def schedule_uninstall():
    """
    Remove the scheduled backup agent.

    This command:
    1. Unloads the agent using launchctl.
    2. Deletes the plist file.
    """
    if not PLIST_PATH.exists():
        console.print("[yellow]No schedule found.[/yellow]")
        return

    try:
        # Unload
        subprocess.run(
            ["launchctl", "bootout", f"gui/{os.getuid()}/{PLIST_LABEL}"],
            capture_output=True,
        )

        # Remove file
        PLIST_PATH.unlink()
        console.print("[bold green]Success![/bold green] Schedule removed.")

    except Exception as e:
        console.print(f"[bold red]Error removing schedule:[/bold red] {e}")
        raise typer.Exit(code=1)
