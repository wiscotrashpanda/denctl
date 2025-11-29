"""Auth storage module for managing credentials.

This module handles reading and writing credentials using a backend abstraction.
By default, credentials are stored in macOS Keychain, but the backend can be
injected for testing purposes.
"""

from den.keychain_backend import KeychainBackend, MacOSKeychainBackend

# Global backend instance - defaults to MacOSKeychainBackend
_backend: KeychainBackend = MacOSKeychainBackend()


def set_backend(backend: KeychainBackend) -> None:
    """Set the storage backend (for testing).

    Args:
        backend: The backend to use for credential storage.
    """
    global _backend
    _backend = backend


def load_credentials() -> dict[str, str]:
    """Load all credentials from the backend.

    Returns:
        Dictionary of credentials, or empty dict if no credentials exist.

    Raises:
        KeychainAccessError: If the backend cannot be accessed.
    """
    credentials = {}
    for key in _backend.list_credentials():
        value = _backend.get_credential(key)
        if value is not None:
            credentials[key] = value
    return credentials


def save_credentials(credentials: dict[str, str]) -> None:
    """Save multiple credentials to the backend.

    Args:
        credentials: Dictionary of credentials to save.

    Raises:
        KeychainAccessError: If credentials cannot be stored.
    """
    for key, value in credentials.items():
        _backend.set_credential(key, value)


def save_credential(key: str, value: str) -> None:
    """Save a single credential to the backend.

    Args:
        key: The credential key (e.g., "anthropic_api_key").
        value: The credential value.

    Raises:
        KeychainAccessError: If the credential cannot be stored.
    """
    _backend.set_credential(key, value)


def delete_credential(key: str) -> None:
    """Delete a credential from the backend.

    Args:
        key: The credential key to delete.

    Raises:
        KeychainAccessError: If the credential cannot be deleted.
    """
    _backend.delete_credential(key)
