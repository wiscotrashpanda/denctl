# den

A CLI utility for local machine automations, built with Python and Typer.

## Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

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

### Install as Standalone Executable (Recommended)

For a standalone installation that doesn't require Python to be installed on the target system, use the installation script.

**Requirements**: Python 3.12 or higher, pip (Python package installer)

#### Build and Install

```bash
# Clone the repository
git clone <repository-url>
cd den

# Run the installation script
./install.sh
```

The installation script will:

1. Check for required dependencies (Python 3, pip)
2. Install PyInstaller if not already present
3. Build the standalone executable using PyInstaller
4. Create the `~/Local` directory if it doesn't exist
5. Copy the executable to `~/Local/den`
6. Create a symbolic link from `/usr/local/bin/den` to `~/Local/den` (requires sudo)
7. Verify the installation

#### Installation Locations

- **Binary location**: `~/Local/den` - The actual executable binary
- **Symlink location**: `/usr/local/bin/den` - Symbolic link for PATH access

#### Exit Codes

The installation script uses the following exit codes:

- `0` - Success
- `1` - Missing dependencies (Python or pip)
- `2` - Build failed
- `3` - Installation failed

## Usage

### Hello Command

The `hello` command greets a user by name.

```bash
# Default greeting
den hello
# Output: Hello, World!

# Custom name greeting
den hello --name Alice
# Output: Hello, Alice!
```

### Help

```bash
# Show available commands
den --help

# Show hello command options
den hello --help

# Show version
den --version
```

## Development Setup

### Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd den

# Install with development dependencies
uv pip install -e ".[dev]"
```

### Run Tests

```bash
uv run pytest
```

### Project Structure

```text
den/
├── src/
│   └── den/
│       ├── __init__.py
│       ├── main.py
│       └── commands/
│           └── hello.py
├── tests/
├── pyproject.toml
└── README.md
```

## License

MIT
