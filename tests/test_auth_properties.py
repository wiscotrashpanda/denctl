"""Property-based tests for the auth storage module.

These tests use hypothesis to verify universal properties across all inputs.
"""

import json

from hypothesis import given, settings, strategies as st

from den import auth_storage
from den.auth_storage import (
    load_credentials,
    save_credential,
    save_credentials,
)
from den.commands.auth import validate_api_key
from den.keychain_backend import InMemoryBackend


# Strategy for generating valid credential keys (non-empty strings without control chars)
credential_key_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "S"),
        blacklist_characters=("\x00", "\n", "\r"),
    ),
)

# Strategy for generating valid credential values (non-empty strings)
credential_value_strategy = st.text(
    min_size=1,
    max_size=200,
    alphabet=st.characters(blacklist_categories=("Cs",)),
)

# Strategy for generating credential dictionaries
credentials_dict_strategy = st.dictionaries(
    keys=credential_key_strategy,
    values=credential_value_strategy,
    min_size=0,
    max_size=10,
)


@settings(max_examples=100)
@given(credentials=credentials_dict_strategy)
def test_property_credential_serialization_round_trip(credentials: dict[str, str]):
    """**Feature: auth-login, Property 3: Credential serialization round-trip**

    *For any* valid credentials dictionary, serializing to JSON and
    deserializing back SHALL produce an equivalent dictionary.

    **Validates: Requirements 3.7**
    """
    # Serialize to JSON string
    serialized = json.dumps(credentials)

    # Deserialize back
    deserialized = json.loads(serialized)

    assert credentials == deserialized


@settings(max_examples=100)
@given(credentials=credentials_dict_strategy)
def test_property_bulk_save_and_load_consistency(credentials: dict[str, str]):
    """**Feature: keychain-storage, Property 3: Bulk Save and Load Consistency**

    *For any* dictionary of credentials, saving them with save_credentials and then
    calling load_credentials SHALL return a dictionary containing all the saved
    credentials with their exact values.

    **Validates: Requirements 2.2, 2.3**
    """
    # Use InMemoryBackend for testing
    backend = InMemoryBackend()
    auth_storage.set_backend(backend)

    # Save all credentials
    save_credentials(credentials)

    # Load and verify
    loaded = load_credentials()
    assert loaded == credentials


@settings(max_examples=100)
@given(
    existing_credentials=credentials_dict_strategy,
    new_key=credential_key_strategy,
    new_value=credential_value_strategy,
)
def test_property_credential_merge_preserves_existing_keys(
    existing_credentials: dict[str, str],
    new_key: str,
    new_value: str,
):
    """**Feature: auth-login, Property 2: Credential merge preserves existing keys**

    *For any* existing credentials and any new credential being saved,
    the save operation SHALL preserve all existing keys while adding or
    updating the new key.

    **Validates: Requirements 3.4**
    """
    # Use InMemoryBackend for testing
    backend = InMemoryBackend()
    auth_storage.set_backend(backend)

    # Set up existing credentials
    if existing_credentials:
        save_credentials(existing_credentials)

    # Save a new credential
    save_credential(new_key, new_value)

    # Load and verify
    result = load_credentials()

    # All existing keys should be preserved
    for key in existing_credentials:
        if key != new_key:
            assert key in result
            assert result[key] == existing_credentials[key]

    # New key should be present with new value
    assert new_key in result
    assert result[new_key] == new_value


@settings(max_examples=100)
@given(
    key=credential_key_strategy,
    value=credential_value_strategy,
)
def test_property_credential_read_write_consistency(
    key: str,
    value: str,
):
    """**Feature: auth-login, Property 4: Credential read/write consistency**

    *For any* credential key-value pair that is saved, reading that key
    from storage SHALL return the same value that was saved.

    **Validates: Requirements 4.2, 4.3**
    """
    # Use InMemoryBackend for testing
    backend = InMemoryBackend()
    auth_storage.set_backend(backend)

    # Save a credential
    save_credential(key, value)

    # Read it back
    credentials = load_credentials()

    # The value should be exactly what we saved
    assert key in credentials
    assert credentials[key] == value


# Strategy for generating non-empty strings (at least one non-whitespace character)
non_empty_string_strategy = st.text(min_size=1).filter(lambda s: len(s.strip()) > 0)

# Strategy for generating whitespace-only strings
whitespace_only_strategy = st.text(
    alphabet=st.sampled_from([" ", "\t", "\n", "\r"]),
    min_size=0,
    max_size=20,
)


@settings(max_examples=100)
@given(api_key=non_empty_string_strategy)
def test_property_non_empty_api_key_acceptance(api_key: str):
    """**Feature: auth-login, Property 1: Non-empty API key acceptance**

    *For any* non-empty string provided as an API key, the validation
    function SHALL accept it as valid input.

    **Validates: Requirements 2.3**
    """
    assert validate_api_key(api_key) is True


@settings(max_examples=100)
@given(whitespace=whitespace_only_strategy)
def test_property_empty_or_whitespace_api_key_rejection(whitespace: str):
    """Property test for empty/whitespace API key rejection.

    *For any* empty string or whitespace-only string, the validation
    function SHALL reject it as invalid input.

    This is the inverse property that complements Property 1.
    """
    assert validate_api_key(whitespace) is False
