#!/bin/bash
#
# Installation script for den CLI executable
#
# This script builds the den CLI as a standalone executable using PyInstaller
# and installs it to ~/Local/den with a symlink at /usr/local/bin/den.
#
# Usage: ./install.sh
#
# Exit codes:
#   0 - Success
#   1 - Missing dependencies
#   2 - Build failed
#   3 - Installation failed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Installation paths
BINARY_DIR="$HOME/Local"
BINARY_PATH="$BINARY_DIR/den"
SYMLINK_PATH="/usr/local/bin/den"

# Print colored status messages
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================================
# Dependency Checks
# ============================================================================

info "Checking dependencies..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    error "Python 3 is required but not installed."
    error "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
info "Found $PYTHON_VERSION"

# Check for pip
if ! python3 -m pip --version &> /dev/null; then
    error "pip is required but not installed."
    error "Please install pip: python3 -m ensurepip --upgrade"
    exit 1
fi

info "Found pip: $(python3 -m pip --version 2>&1 | head -1)"

# Check for PyInstaller, install if not present
if ! python3 -m PyInstaller --version &> /dev/null; then
    warn "PyInstaller not found. Installing..."
    if ! python3 -m pip install pyinstaller; then
        error "Failed to install PyInstaller."
        error "Please install manually: pip install pyinstaller"
        exit 1
    fi
    info "PyInstaller installed successfully."
else
    info "Found PyInstaller: $(python3 -m PyInstaller --version 2>&1)"
fi

# Check for spec file
if [ ! -f "den.spec" ]; then
    error "den.spec file not found in current directory."
    error "Please run this script from the project root directory."
    exit 1
fi

info "All dependencies satisfied."
echo ""

# ============================================================================
# Build Process
# ============================================================================

info "Building den executable with PyInstaller..."
echo ""

# Clean previous builds
if [ -d "dist" ]; then
    info "Cleaning previous build artifacts..."
    rm -rf dist
fi

if [ -d "build" ]; then
    rm -rf build
fi

# Run PyInstaller
if ! python3 -m PyInstaller den.spec; then
    error "PyInstaller build failed."
    error "Check the output above for details."
    exit 2
fi

# Verify build output
if [ ! -f "dist/den" ]; then
    error "Build completed but executable not found at dist/den"
    exit 2
fi

info "Build completed successfully."
echo ""

# ============================================================================
# Installation
# ============================================================================

info "Installing den executable..."

# Create ~/Local directory if it doesn't exist
if [ ! -d "$BINARY_DIR" ]; then
    info "Creating directory: $BINARY_DIR"
    if ! mkdir -p "$BINARY_DIR"; then
        error "Failed to create directory: $BINARY_DIR"
        exit 3
    fi
fi

# Copy executable to ~/Local/den
info "Copying executable to $BINARY_PATH"
if ! cp "dist/den" "$BINARY_PATH"; then
    error "Failed to copy executable to $BINARY_PATH"
    exit 3
fi

# Make sure it's executable
chmod +x "$BINARY_PATH"

# Create symbolic link in /usr/local/bin
info "Creating symbolic link at $SYMLINK_PATH"
info "This requires administrator privileges..."

# Remove existing symlink if present
if [ -L "$SYMLINK_PATH" ]; then
    warn "Removing existing symlink at $SYMLINK_PATH"
    if ! sudo rm "$SYMLINK_PATH"; then
        error "Failed to remove existing symlink at $SYMLINK_PATH"
        exit 3
    fi
elif [ -f "$SYMLINK_PATH" ]; then
    error "A file (not a symlink) already exists at $SYMLINK_PATH"
    error "Please remove it manually and run this script again."
    exit 3
fi

# Create the symlink
if ! sudo ln -s "$BINARY_PATH" "$SYMLINK_PATH"; then
    error "Failed to create symbolic link at $SYMLINK_PATH"
    error "You may need to manually create the symlink:"
    error "  sudo ln -s $BINARY_PATH $SYMLINK_PATH"
    exit 3
fi

info "Symbolic link created successfully."
echo ""

# ============================================================================
# Verification
# ============================================================================

info "Verifying installation..."

# Check if den command is accessible
if ! command -v den &> /dev/null; then
    error "Verification failed: 'den' command not found in PATH."
    error "You may need to restart your terminal or add /usr/local/bin to your PATH."
    exit 3
fi

# Test the executable
if den --help &> /dev/null; then
    info "Verification successful: 'den' command is working."
else
    warn "The 'den' command was found but may not be working correctly."
    warn "Try running 'den --help' to check for errors."
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Installation completed successfully!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "  Binary location: $BINARY_PATH"
echo "  Symlink location: $SYMLINK_PATH"
echo ""
echo "  Try running: den hello"
echo ""

exit 0
