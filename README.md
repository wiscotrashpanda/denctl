# den

**den** 🦝 - A Python CLI automation tool for macOS built with Typer.

## Overview

**den** is a command-line interface application designed to house various automation tasks for local macOS development. Built with modern Python tooling including [uv](https://github.com/astral-sh/uv) for package management and [Typer](https://typer.tiangolo.com/) for CLI functionality.

## Features

- Fast and modern Python CLI using Typer
- Beautiful terminal output with Rich
- Managed with uv for blazing-fast dependency resolution
- Comprehensive test coverage with pytest
- Code linting and formatting with Ruff
- Static type checking with MyPy


## Installation

### Prerequisites

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) package manager

### Install with uv

```bash
# Clone the repository
git clone git@github.com:wiscotrashpanda/den.git
cd den

# Install dependencies
uv sync

# Run via uv
uv run den hello
```

### Install as standalone command

```bash
# Install in editable mode
uv pip install -e .

# Now you can use directly (within activated venv)
.venv/bin/den hello
```

## Usage

### Homebrew Backups

**den** provides automated backups for your Homebrew configuration to a private GitHub Gist, optionally formatted by Claude AI.

#### Prerequisites

*   GitHub CLI (`gh`) installed and authenticated
*   Anthropic API Key (for AI formatting)

#### Setup

1.  **Authenticate Anthropic API:**
    ```bash
    uv run den auth anthropic
    # Follow the prompt to enter your 'sk-...' key
    ```

2.  **Run Manual Backup:**
    ```bash
    uv run den homebrew backup
    ```

#### Options

*   `--force`, `-f`: Force backup even if no changes are detected.
*   `--dry-run`: Generate and format the Brewfile without uploading.
*   `--no-format`: Skip the AI formatting step.

#### Automated Scheduling

You can schedule automated daily backups using launchd:

```bash
# Install scheduled backup (runs daily at 06:00 UTC)
uv run den homebrew schedule install

# Remove scheduled backup
uv run den homebrew schedule uninstall
```

Logs are stored in `~/Library/Logs/den.homebrew.log` and `~/Library/Logs/den.homebrew.error.log`.

### Hello Command

The MVP includes a simple `hello` command that greets a user:

```bash
# Using default name
uv run den hello
# Output: Hello World!

# Using custom name
uv run den hello Josh
# Output: Hello Josh!


```

### Help

```bash
# Main help
uv run den --help

# Command-specific help
uv run den hello --help
```

## Development

### Setup Development Environment

```bash
# Clone and navigate to the repository
git clone git@github.com:wiscotrashpanda/den.git
cd den

# Install dependencies including dev dependencies
uv sync
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run with coverage (requires pytest-cov)
uv run pytest tests/ --cov
```

### Code Quality

This project uses Ruff for linting and formatting, and MyPy for type checking:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy .
```

## Project Structure

```
den/
├── src/
│   └── denctl/
│       ├── __init__.py          # Package initialization
│       ├── main.py              # Main CLI entry point
│       └── commands/
│           ├── __init__.py
│           ├── auth.py          # Authentication management
│           ├── hello.py         # Hello command logic
│           └── homebrew.py      # Homebrew backup functionality
├── tests/
│   ├── __init__.py
│   └── test_hello.py            # Test suite
├── pyproject.toml               # Project configuration
├── uv.lock                      # Dependency lock file
├── CLAUDE.MD                    # Claude Code guidelines
└── README.md                    # This file
```

## Contributing

This is a personal automation tool, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure tests pass (`uv run pytest tests/`)
5. Format and lint code (`uv run ruff format .` and `uv run ruff check .`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is for personal use. Feel free to adapt for your own needs.

## Author

**Josh Butler** (@wiscotrashpanda)
