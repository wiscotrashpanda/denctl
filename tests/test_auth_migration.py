"""Unit and property-based tests for the auth migration module.

These tests verify the migration of credentials from auth.json to Keychain.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given, settings, strategies as st

from den.auth_migration import get_legacy_auth_file_path, migrate_from_json
from den.keychain_backend import InMemoryBackend, KeychainAccessError


class TestGetLegacyAuthFilePath:
    """Tests for get_legacy_auth_file_path function."""

    def test_returns_correct_path(self) -> None:
        """Test that get_legacy_auth_file_path returns ~/.config/den/auth.json."""
        result = get_legacy_auth_file_path()
        expected = Path.home() / ".config" / "den" / "auth.json"
        assert result == expected


class TestMigrateFromJson:
    """Tests for migrate_from_json function."""

    def test_no_migration_when_auth_json_missing(self) -> None:
        """Test that migration returns False when auth.json doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth_file = Path(tmpdir) / "auth.json"
            backend = InMemoryBackend()

            with patch(
                "den.auth_migration.get_legacy_auth_file_path", return_value=auth_file
            ):
                result = migrate_from_json(backend)

            assert result is False
            assert backend.list_credentials() == []

    def test_migration_transfers_credentials(self) -> None:
        """Test that migration transfers credentials to Keychain."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth_file = Path(tmpdir) / "auth.json"
            credentials = {
                "anthropic_api_key": "test_key",
                "github_token": "test_token",
            }

            # Create auth.json with credentials
            with auth_file.open("w", encoding="utf-8") as f:
                json.dump(credentials, f)

            backend = InMemoryBackend()

            with patch(
                "den.auth_migration.get_legacy_auth_file_path", return_value=auth_file
            ):
                result = migrate_from_json(backend)

            # Verify migration occurred
            assert result is True
            # Verify credentials were transferred
            assert backend.get_credential("anthropic_api_key") == "test_key"
            assert backend.get_credential("github_token") == "test_token"
            # Verify auth.json was deleted
            assert not auth_file.exists()

    def test_migration_preserves_existing_keychain_credentials(self) -> None:
        """Test that migration doesn't overwrite existing Keychain credentials."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth_file = Path(tmpdir) / "auth.json"
            auth_credentials = {"anthropic_api_key": "old_key"}

            # Create auth.json
            with auth_file.open("w", encoding="utf-8") as f:
                json.dump(auth_credentials, f)

            backend = InMemoryBackend()
            # Pre-populate Keychain with different value
            backend.set_credential("anthropic_api_key", "existing_key")

            with patch(
                "den.auth_migration.get_legacy_auth_file_path", return_value=auth_file
            ):
                result = migrate_from_json(backend)

            # Verify migration occurred
            assert result is True
            # Verify existing credential was NOT overwritten
            assert backend.get_credential("anthropic_api_key") == "existing_key"
            # Verify auth.json was still deleted
            assert not auth_file.exists()

    def test_migration_handles_invalid_json(self) -> None:
        """Test that migration handles invalid JSON gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth_file = Path(tmpdir) / "auth.json"

            # Create auth.json with invalid JSON
            with auth_file.open("w", encoding="utf-8") as f:
                f.write("not valid json {")

            backend = InMemoryBackend()

            with patch(
                "den.auth_migration.get_legacy_auth_file_path", return_value=auth_file
            ):
                result = migrate_from_json(backend)

            # Verify migration was skipped
            assert result is False
            # Verify auth.json was preserved
            assert auth_file.exists()
            # Verify no credentials were added
            assert backend.list_credentials() == []

    def test_migration_handles_non_dict_json(self) -> None:
        """Test that migration handles non-dictionary JSON gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth_file = Path(tmpdir) / "auth.json"

            # Create auth.json with a list instead of dict
            with auth_file.open("w", encoding="utf-8") as f:
                json.dump(["not", "a", "dict"], f)

            backend = InMemoryBackend()

            with patch(
                "den.auth_migration.get_legacy_auth_file_path", return_value=auth_file
            ):
                result = migrate_from_json(backend)

            # Verify migration was skipped
            assert result is False
            # Verify auth.json was preserved
            assert auth_file.exists()
            # Verify no credentials were added
            assert backend.list_credentials() == []

    def test_migration_handles_empty_credentials(self) -> None:
        """Test that migration handles empty credentials dictionary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth_file = Path(tmpdir) / "auth.json"

            # Create auth.json with empty dict
            with auth_file.open("w", encoding="utf-8") as f:
                json.dump({}, f)

            backend = InMemoryBackend()

            with patch(
                "den.auth_migration.get_legacy_auth_file_path", return_value=auth_file
            ):
                result = migrate_from_json(backend)

            # Verify migration occurred (even though no credentials)
            assert result is True
            # Verify auth.json was deleted
            assert not auth_file.exists()
            # Verify no credentials were added
            assert backend.list_credentials() == []


# Property-based tests
@settings(max_examples=100)
@given(
    credentials=st.dictionaries(
        keys=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        values=st.text(min_size=0, max_size=500),
        min_size=0,
        max_size=10,
    )
)
def test_property_migration_transfers_and_cleans_up(
    credentials: dict[str, str],
) -> None:
    """Property 4: Migration Transfers and Cleans Up.

    **Feature: keychain-storage, Property 4: Migration Transfers and Cleans Up**
    **Validates: Requirements 4.1, 4.2**

    For any set of credentials stored in auth.json, running migration SHALL
    result in all credentials being accessible via the Keychain backend, and
    the auth.json file SHALL be deleted.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        auth_file = Path(tmpdir) / "auth.json"

        # Create auth.json with credentials
        with auth_file.open("w", encoding="utf-8") as f:
            json.dump(credentials, f)

        backend = InMemoryBackend()

        with patch(
            "den.auth_migration.get_legacy_auth_file_path", return_value=auth_file
        ):
            result = migrate_from_json(backend)

        # Verify migration occurred
        assert result is True

        # Verify all credentials are accessible in Keychain
        for key, value in credentials.items():
            assert backend.get_credential(key) == value

        # Verify auth.json was deleted
        assert not auth_file.exists()


@settings(max_examples=100)
@given(
    auth_credentials=st.dictionaries(
        keys=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        values=st.text(min_size=0, max_size=500),
        min_size=1,
        max_size=5,
    ),
    existing_credentials=st.dictionaries(
        keys=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        values=st.text(min_size=0, max_size=500),
        min_size=1,
        max_size=5,
    ),
)
def test_property_migration_preserves_existing_keychain_credentials(
    auth_credentials: dict[str, str], existing_credentials: dict[str, str]
) -> None:
    """Property 5: Migration Preserves Existing Keychain Credentials.

    **Feature: keychain-storage, Property 5: Migration Preserves Existing Keychain Credentials**
    **Validates: Requirements 4.4**

    For any credential that already exists in the Keychain, migration SHALL NOT
    overwrite it with a value from auth.json.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        auth_file = Path(tmpdir) / "auth.json"

        # Create auth.json with credentials
        with auth_file.open("w", encoding="utf-8") as f:
            json.dump(auth_credentials, f)

        backend = InMemoryBackend()

        # Pre-populate Keychain with existing credentials
        for key, value in existing_credentials.items():
            backend.set_credential(key, value)

        with patch(
            "den.auth_migration.get_legacy_auth_file_path", return_value=auth_file
        ):
            migrate_from_json(backend)

        # Verify existing credentials were NOT overwritten
        for key, value in existing_credentials.items():
            assert backend.get_credential(key) == value

        # Verify new credentials from auth.json were added
        for key, value in auth_credentials.items():
            if key not in existing_credentials:
                assert backend.get_credential(key) == value
