"""Unit tests for the auth storage module.

Tests for auth storage functions with keychain backend.
"""

from den import auth_storage
from den.auth_storage import (
    load_credentials,
    save_credential,
    save_credentials,
    delete_credential,
)
from den.keychain_backend import InMemoryBackend


def test_load_credentials_returns_empty_dict_when_no_credentials():
    """Test that load_credentials returns empty dict when no credentials exist."""
    backend = InMemoryBackend()
    auth_storage.set_backend(backend)

    result = load_credentials()
    assert result == {}


def test_save_and_load_single_credential():
    """Test that a single credential can be saved and loaded."""
    backend = InMemoryBackend()
    auth_storage.set_backend(backend)

    save_credential("test_key", "test_value")
    result = load_credentials()
    assert result == {"test_key": "test_value"}


def test_save_credentials_stores_multiple():
    """Test that save_credentials stores multiple credentials."""
    backend = InMemoryBackend()
    auth_storage.set_backend(backend)

    credentials = {
        "anthropic_api_key": "test_anthropic_key",
        "github_token": "test_github_token",
    }
    save_credentials(credentials)

    result = load_credentials()
    assert result == credentials


def test_save_credential_preserves_existing():
    """Test that save_credential preserves existing credentials."""
    backend = InMemoryBackend()
    auth_storage.set_backend(backend)

    save_credential("key1", "value1")
    save_credential("key2", "value2")

    result = load_credentials()
    assert result == {"key1": "value1", "key2": "value2"}


def test_delete_credential_removes_credential():
    """Test that delete_credential removes a credential."""
    backend = InMemoryBackend()
    auth_storage.set_backend(backend)

    save_credential("test_key", "test_value")
    delete_credential("test_key")

    result = load_credentials()
    assert result == {}


def test_delete_nonexistent_credential_does_not_raise():
    """Test that deleting a non-existent credential does not raise an error."""
    backend = InMemoryBackend()
    auth_storage.set_backend(backend)

    # Should not raise
    delete_credential("nonexistent_key")
