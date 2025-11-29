"""Unit tests for the keychain backend module.

These tests verify the KeychainBackend implementations using both
unit tests and property-based tests with Hypothesis.
"""

import pytest
from hypothesis import given, settings, strategies as st

from den.keychain_backend import (
    InMemoryBackend,
    KeychainAccessError,
    KeychainBackend,
    MacOSKeychainBackend,
)


class TestInMemoryBackend:
    """Tests for InMemoryBackend implementation."""

    def test_get_nonexistent_credential_returns_none(self) -> None:
        """Test that getting a non-existent credential returns None."""
        backend = InMemoryBackend()
        result = backend.get_credential("nonexistent_key")
        assert result is None

    def test_set_and_get_credential(self) -> None:
        """Test that credentials can be stored and retrieved."""
        backend = InMemoryBackend()
        backend.set_credential("test_key", "test_value")
        result = backend.get_credential("test_key")
        assert result == "test_value"

    def test_delete_credential(self) -> None:
        """Test that credentials can be deleted."""
        backend = InMemoryBackend()
        backend.set_credential("test_key", "test_value")
        backend.delete_credential("test_key")
        result = backend.get_credential("test_key")
        assert result is None

    def test_delete_nonexistent_credential_does_not_raise(self) -> None:
        """Test that deleting a non-existent credential does not raise an error."""
        backend = InMemoryBackend()
        # Should not raise
        backend.delete_credential("nonexistent_key")

    def test_list_credentials_empty(self) -> None:
        """Test that list_credentials returns empty list for new backend."""
        backend = InMemoryBackend()
        result = backend.list_credentials()
        assert result == []

    def test_list_credentials_with_data(self) -> None:
        """Test that list_credentials returns all stored keys."""
        backend = InMemoryBackend()
        backend.set_credential("key1", "value1")
        backend.set_credential("key2", "value2")
        result = backend.list_credentials()
        assert set(result) == {"key1", "key2"}


class TestMacOSKeychainBackend:
    """Tests for MacOSKeychainBackend implementation."""

    def test_service_name_is_den_cli(self) -> None:
        """Test that the service name is set to 'den-cli'."""
        backend = MacOSKeychainBackend()
        assert backend.SERVICE_NAME == "den-cli"

    def test_set_credential_with_empty_key_raises_value_error(self) -> None:
        """Test that setting a credential with an empty key raises ValueError."""
        backend = MacOSKeychainBackend()
        with pytest.raises(ValueError, match="Credential key cannot be empty"):
            backend.set_credential("", "test_value")

    def test_set_credential_with_whitespace_key_raises_value_error(self) -> None:
        """Test that setting a credential with a whitespace-only key raises ValueError."""
        backend = MacOSKeychainBackend()
        with pytest.raises(ValueError, match="Credential key cannot be empty"):
            backend.set_credential("   ", "test_value")


@settings(max_examples=100)
@given(
    key=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    value=st.text(min_size=0, max_size=1000),
)
def test_property_credential_roundtrip_consistency(key: str, value: str) -> None:
    """Property 1: Credential Round-Trip Consistency.

    **Feature: keychain-storage, Property 1: Credential Round-Trip Consistency**
    **Validates: Requirements 1.1, 1.2**

    For any valid credential key-value pair, saving the credential and then
    retrieving it SHALL return the exact same value.
    """
    backend = InMemoryBackend()
    backend.set_credential(key, value)
    retrieved = backend.get_credential(key)
    assert retrieved == value


@settings(max_examples=100)
@given(
    key=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    value=st.text(min_size=0, max_size=1000),
)
def test_property_delete_removes_credential(key: str, value: str) -> None:
    """Property 2: Delete Removes Credential.

    **Feature: keychain-storage, Property 2: Delete Removes Credential**
    **Validates: Requirements 1.3**

    For any credential that has been saved, deleting it and then attempting to
    retrieve it SHALL return None.
    """
    backend = InMemoryBackend()
    backend.set_credential(key, value)
    backend.delete_credential(key)
    retrieved = backend.get_credential(key)
    assert retrieved is None


@settings(max_examples=100)
@given(
    key1=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    value1=st.text(min_size=0, max_size=1000),
    key2=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    value2=st.text(min_size=0, max_size=1000),
)
def test_property_credentials_are_isolated(
    key1: str, value1: str, key2: str, value2: str
) -> None:
    """Test that credentials with different keys are isolated from each other.

    Setting one credential should not affect another credential, even if they
    have similar keys.
    """
    # Skip if keys are the same
    if key1 == key2:
        return

    backend = InMemoryBackend()
    backend.set_credential(key1, value1)
    backend.set_credential(key2, value2)

    # Both should be retrievable with their original values
    assert backend.get_credential(key1) == value1
    assert backend.get_credential(key2) == value2

    # Deleting one should not affect the other
    backend.delete_credential(key1)
    assert backend.get_credential(key1) is None
    assert backend.get_credential(key2) == value2


@settings(max_examples=100)
@given(
    credentials=st.dictionaries(
        keys=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        values=st.text(min_size=0, max_size=500),
        min_size=0,
        max_size=10,
    )
)
def test_property_list_credentials_returns_all_keys(
    credentials: dict[str, str],
) -> None:
    """Test that list_credentials returns all stored credential keys.

    After setting multiple credentials, list_credentials should return all keys.
    """
    backend = InMemoryBackend()

    for key, value in credentials.items():
        backend.set_credential(key, value)

    listed_keys = backend.list_credentials()
    assert set(listed_keys) == set(credentials.keys())
