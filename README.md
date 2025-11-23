# denctl

**denctl** (🦝) - A Python CLI automation tool for macOS built with Typer.

## Overview

denctl is a command-line interface application designed to house various automation tasks for local macOS development. Built with modern Python tooling including [uv](https://github.com/astral-sh/uv) for package management and [Typer](https://typer.tiangolo.com/) for CLI functionality.

The tool can be invoked using either `denctl` or `den` for convenience.

## Features

- Fast and modern Python CLI using Typer
- Managed with uv for blazing-fast dependency resolution
- Comprehensive test coverage with pytest
- Code formatting with Black
- Dual command aliases: `denctl` and `den`

## Installation

### Prerequisites

- Python >= 3.14
- [uv](https://github.com/astral-sh/uv) package manager

### Install with uv

```bash
# Clone the repository
git clone git@github.com:wiscotrashpanda/denctl.git
cd denctl

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
.venv/bin/denctl hello
```

## Usage

### Hello Command

The MVP includes a simple `hello` command that greets a user:

```bash
# Using default name
uv run den hello
# Output: Hello World!

# Using custom name
uv run den hello Josh
# Output: Hello Josh!

# Using denctl alias
uv run denctl hello wiscotrashpanda
# Output: Hello wiscotrashpanda!
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
git clone git@github.com:wiscotrashpanda/denctl.git
cd denctl

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

### Code Formatting

This project uses Black for code formatting:

```bash
# Check formatting
uv run black --check src/denctl/

# Format code
uv run black src/denctl/
```

## Project Structure

```
denctl/
├── src/
│   └── denctl/
│       └── __init__.py          # Main CLI application
├── tests/
│   ├── __init__.py
│   └── test_hello.py            # Test suite
├── .vscode/
│   └── settings.json            # VS Code configuration
├── pyproject.toml               # Project configuration
├── uv.lock                      # Dependency lock file
└── README.md                    # This file
```

## Contributing

This is a personal automation tool, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure tests pass (`uv run pytest tests/`)
5. Format code (`uv run black src/denctl/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is for personal use. Feel free to adapt for your own needs.

## Author

**Josh Butler** (@wiscotrashpanda)
