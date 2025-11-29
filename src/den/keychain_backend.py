"""Keychain backend abstraction for credential storage.

This module defines the backend interface for credential storage and provides
implementations for production (macOS Keychain) and testing (in-memory).
"""

import json
from typing import Protocol

import keyring


class KeychainAccessError(Exception):
    """Exception raised when Keychain access fails.

    Attributes:
        message: Error message describing the failure.
        original_error: The underlying exception that caused the failure.
    """

    def __init__(self, message: str, original_error: Exception | None = None):
        """Initialize KeychainAccessError.

        Args:
            message: Error message describing the failure.
            original_error: The underlying exception that caused the failure.
        """
        super().__init__(message)
        self.original_error = original_error


class KeychainBackend(Protocol):
    """Protocol defining the interface for credential storage backends."""

    def get_credential(self, key: str) -> str | None:
        """Retrieve a credential by key.

        Args:
            key: The credential key to retrieve.

        Returns:
            The credential value, or None if not found.
        """
        ...

    def set_credential(self, key: str, value: str) -> None:
        """Store a credential with the given key.

        Args:
            key: The credential key.
            value: The credential value to store.

        Raises:
            KeychainAccessError: If the credential cannot be stored.
        """
        ...

    def delete_credential(self, key: str) -> None:
        """Delete a credential by key.

        Args:
            key: The credential key to delete.

        Raises:
            KeychainAccessError: If the credential cannot be deleted.
        """
        ...

    def list_credentials(self) -> list[str]:
        """List all credential keys stored for this service.

        Returns:
            List of credential keys.

        Raises:
            KeychainAccessError: If credentials cannot be listed.
        """
        ...


class InMemoryBackend:
    """In-memory backend for testing without Keychain access.

    This backend stores credentials in a dictionary for testing purposes.
    """

    def __init__(self):
        """Initialize the in-memory backend with an empty store."""
        self._store: dict[str, str] = {}

    def get_credential(self, key: str) -> str | None:
        """Retrieve a credential by key.

        Args:
            key: The credential key to retrieve.

        Returns:
            The credential value, or None if not found.
        """
        return self._store.get(key)

    def set_credential(self, key: str, value: str) -> None:
        """Store a credential with the given key.

        Args:
            key: The credential key.
            value: The credential value to store.
        """
        self._store[key] = value

    def delete_credential(self, key: str) -> None:
        """Delete a credential by key.

        Args:
            key: The credential key to delete.
        """
        self._store.pop(key, None)

    def list_credentials(self) -> list[str]:
        """List all credential keys stored for this service.

        Returns:
            List of credential keys.
        """
        return list(self._store.keys())


class MacOSKeychainBackend:
    """Production backend using macOS Keychain via keyring library."""

    SERVICE_NAME = "den-cli"
    REGISTRY_KEY = "_credential_registry"

    def __init__(self):
        """Initialize the macOS Keychain backend."""
        pass

    def get_credential(self, key: str) -> str | None:
        """Retrieve a credential from the Keychain.

        Args:
            key: The credential key to retrieve.

        Returns:
            The credential value, or None if not found.

        Raises:
            KeychainAccessError: If Keychain access fails.
        """
        try:
            return keyring.get_password(self.SERVICE_NAME, key)
        except keyring.errors.KeyringError as e:
            raise KeychainAccessError(
                f"Failed to retrieve credential from Keychain: {e}",
                original_error=e,
            ) from e

    def set_credential(self, key: str, value: str) -> None:
        """Store a credential in the Keychain.

        Args:
            key: The credential key.
            value: The credential value to store.

        Raises:
            KeychainAccessError: If Keychain access fails.
        """
        if not key or not key.strip():
            raise ValueError("Credential key cannot be empty")

        try:
            keyring.set_password(self.SERVICE_NAME, key, value)
            self._update_registry(key, add=True)
        except keyring.errors.KeyringError as e:
            raise KeychainAccessError(
                f"Failed to store credential in Keychain: {e}",
                original_error=e,
            ) from e

    def delete_credential(self, key: str) -> None:
        """Remove a credential from the Keychain.

        Args:
            key: The credential key to delete.

        Raises:
            KeychainAccessError: If Keychain access fails.
        """
        try:
            keyring.delete_password(self.SERVICE_NAME, key)
            self._update_registry(key, add=False)
        except keyring.errors.PasswordDeleteError:
            # Credential doesn't exist - this is not an error
            pass
        except keyring.errors.KeyringError as e:
            raise KeychainAccessError(
                f"Failed to delete credential from Keychain: {e}",
                original_error=e,
            ) from e

    def list_credentials(self) -> list[str]:
        """List all credentials for den-cli service.

        Returns:
            List of credential keys.

        Raises:
            KeychainAccessError: If Keychain access fails.
        """
        try:
            registry_json = keyring.get_password(self.SERVICE_NAME, self.REGISTRY_KEY)
            if registry_json is None:
                return []
            return json.loads(registry_json)
        except json.JSONDecodeError as e:
            raise KeychainAccessError(
                f"Failed to parse credential registry: {e}",
                original_error=e,
            ) from e
        except keyring.errors.KeyringError as e:
            raise KeychainAccessError(
                f"Failed to list credentials from Keychain: {e}",
                original_error=e,
            ) from e

    def _update_registry(self, key: str, add: bool) -> None:
        """Update the credential registry.

        Args:
            key: The credential key to add or remove.
            add: True to add the key, False to remove it.

        Raises:
            KeychainAccessError: If registry update fails.
        """
        try:
            current_keys = set(self.list_credentials())

            if add:
                current_keys.add(key)
            else:
                current_keys.discard(key)

            # Store updated registry
            registry_json = json.dumps(sorted(current_keys))
            keyring.set_password(self.SERVICE_NAME, self.REGISTRY_KEY, registry_json)
        except keyring.errors.KeyringError as e:
            raise KeychainAccessError(
                f"Failed to update credential registry: {e}",
                original_error=e,
            ) from e
