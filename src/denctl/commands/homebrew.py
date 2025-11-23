import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from anthropic import Anthropic, APIError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(name="homebrew", help="Manage Homebrew backups and configuration.")
console = Console()

# Configuration Constants
CONFIG_DIR = Path.home() / ".config" / "denctl"
CONFIG_FILE = CONFIG_DIR / "homebrew.json"
GENERAL_CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def get_general_config() -> Dict[str, Any]:
    """Load general configuration from JSON file."""
    if not GENERAL_CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(GENERAL_CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to JSON file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    # Ensure privacy
    CONFIG_FILE.chmod(0o600)


def check_dependencies():
    """Verify required tools are installed."""
    for cmd in ["brew", "gh"]:
        if subprocess.run(["which", cmd], capture_output=True).returncode != 0:
            console.print(
                f"[bold red]Error:[/bold red] '{cmd}' is not installed or not in PATH."
            )
            raise typer.Exit(code=1)

    # Check if gh is authenticated
    if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
        console.print(
            "[bold red]Error:[/bold red] GitHub CLI is not authenticated. "
            "Run 'gh auth login'."
        )
        raise typer.Exit(code=1)


def generate_brewfile() -> str:
    """Generate Brewfile content using brew bundle dump."""
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
    """Calculate SHA256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_anthropic_api_key() -> Optional[str]:
    """Retrieve Anthropic API key from Env or General Config."""
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
    """Format Brewfile content using Anthropic API."""
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
    """Create or update GitHub Gist."""
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
