# den

A CLI utility for local machine automations, built with Python and Typer.

## Features

- **Homebrew Management**: Upgrade packages and automatically backup your Brewfile to GitHub Gist
- **AI-Powered Formatting**: Uses Anthropic's Claude to format and organize your Brewfile
- **Secure Credential Storage**: Safely store API keys for Anthropic and GitHub
- **Change Detection**: Only backs up when your Brewfile changes (with force override option)

## Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

### Install den (Development Mode)

```bash
# Clone the repository
git clone <repository-url>
cd den

# Install the package
uv pip install -e .
```

### Install as Standalone Executable

For a standalone installation that doesn't require Python on the target system:

```bash
# Clone the repository
git clone <repository-url>
cd den

# Run the installation script
./install.sh
```

The script will build a standalone executable and install it to `~/Local/den` with a symlink at `/usr/local/bin/den`.

#### Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Missing dependencies |
| 2 | Build failed |
| 3 | Installation failed |

## Usage

### Authentication

Configure credentials for external services:

```bash
den auth login
```

This will prompt you to select a provider (Anthropic or GitHub) and securely enter your API key or token. Credentials are stored at `~/.config/den/auth.json`.

### Homebrew Management

Upgrade all Homebrew packages and backup your Brewfile to GitHub Gist:

```bash
# Standard upgrade with conditional backup
den brew upgrade

# Force backup even if Brewfile unchanged
den brew upgrade --force
```

The `brew upgrade` command:
1. Runs `brew upgrade` to update all packages
2. Generates a new Brewfile with `brew bundle dump`
3. Checks if the Brewfile has changed (skips backup if unchanged)
4. Formats the Brewfile using Anthropic's Claude API
5. Creates or updates a private GitHub Gist with the formatted Brewfile
6. Saves state to track changes between runs

Logs are written to `~/.local/share/den/logs/brew.log`.

### Hello Command

A simple greeting command:

```bash
# Default greeting
den hello
# Output: Hello, World!

# Custom name
den hello --name Alice
# Output: Hello, Alice!
```

### Help

```bash
# Show available commands
den --help

# Show command-specific help
den auth --help
den brew --help

# Show version
den --version
```

## Configuration

### Credentials

Credentials are stored at `~/.config/den/auth.json`:

- `anthropic_api_key`: Required for Brewfile formatting
- `github_token`: Required for Gist backup (needs `gist` scope)

### State

Brew state is stored at `~/.local/share/den/state.json`, tracking:

- `brewfile_hash`: Hash of the last backed-up Brewfile
- `gist_id`: ID of the GitHub Gist for updates

## Development

### Setup

```bash
# Clone and install with dev dependencies
git clone <repository-url>
cd den
uv pip install -e ".[dev]"
```

### Run Tests

```bash
uv run pytest
```

### Project Structure

```text
den/
├── src/den/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── auth_storage.py      # Credential management
│   ├── brew_logger.py       # Logging setup
│   ├── brew_runner.py       # Homebrew command execution
│   ├── brewfile_formatter.py # AI-powered formatting
│   ├── gist_client.py       # GitHub Gist API client
│   ├── hash_utils.py        # Content hashing
│   ├── state_storage.py     # State persistence
│   └── commands/
│       ├── auth.py          # Auth commands
│       ├── brew.py          # Brew commands
│       └── hello.py         # Hello command
├── tests/
├── pyproject.toml
└── README.md
```

## License

MIT
