"""Migration module for transferring credentials from auth.json to Keychain.

This module handles the one-time migration of credentials from the legacy
plain-text auth.json file to the secure macOS Keychain storage.
"""

import json
import logging
from pathlib import Path

from den.keychain_backend import KeychainBackend, MacOSKeychainBackend

logger = logging.getLogger(__name__)


def get_legacy_auth_file_path() -> Path:
    """Return the path to the legacy auth.json file.

    Returns:
        Path to ~/.config/den/auth.json
    """
    return Path.home() / ".config" / "den" / "auth.json"


def migrate_from_json(backend: KeychainBackend | None = None) -> bool:
    """Migrate credentials from auth.json to Keychain.

    This function:
    1. Checks if auth.json exists
    2. Loads credentials from auth.json
    3. Migrates each credential to Keychain (skipping existing ones)
    4. Deletes auth.json on successful migration

    Args:
        backend: Optional backend to use (defaults to MacOSKeychainBackend).
                 Primarily for testing.

    Returns:
        True if migration occurred, False if no migration was needed.

    Raises:
        KeychainAccessError: If Keychain operations fail during migration.
    """
    if backend is None:
        backend = MacOSKeychainBackend()

    auth_file = get_legacy_auth_file_path()

    # No migration needed if auth.json doesn't exist
    if not auth_file.exists():
        return False

    logger.info(f"Found legacy auth.json at {auth_file}, starting migration")

    try:
        # Load credentials from auth.json
        with auth_file.open("r", encoding="utf-8") as f:
            credentials = json.load(f)

        if not isinstance(credentials, dict):
            logger.warning(
                f"Invalid auth.json format (not a dictionary), skipping migration"
            )
            return False

        # Migrate each credential
        migrated_count = 0
        for key, value in credentials.items():
            # Skip if credential already exists in Keychain
            existing_value = backend.get_credential(key)
            if existing_value is not None:
                logger.info(f"Credential '{key}' already exists in Keychain, skipping")
                continue

            # Store in Keychain
            backend.set_credential(key, value)
            migrated_count += 1
            logger.info(f"Migrated credential '{key}' to Keychain")

        # Delete auth.json after successful migration
        auth_file.unlink()
        logger.info(
            f"Migration complete: {migrated_count} credentials migrated, "
            f"auth.json deleted"
        )
        return True

    except json.JSONDecodeError as e:
        logger.warning(
            f"Failed to parse auth.json (invalid JSON): {e}, "
            f"preserving file and skipping migration"
        )
        return False
    except Exception as e:
        logger.error(
            f"Migration failed with error: {e}, preserving auth.json", exc_info=True
        )
        # Re-raise to allow caller to handle
        raise
