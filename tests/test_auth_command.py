"""Unit tests for the auth command module.

Tests for provider registry and API key validation.
"""

from den.commands.auth import PROVIDERS, validate_api_key


def test_provider_registry_contains_anthropic():
    """Test that the provider registry includes Anthropic.

    _Requirements: 1.2_
    """
    assert "Anthropic" in PROVIDERS
    provider = PROVIDERS["Anthropic"]
    assert provider.name == "Anthropic"
    assert provider.key_name == "anthropic_api_key"


def test_validate_api_key_rejects_empty_string():
    """Test that validation rejects empty strings.

    _Requirements: 2.4_
    """
    assert validate_api_key("") is False


def test_validate_api_key_rejects_whitespace_only():
    """Test that validation rejects whitespace-only strings.

    _Requirements: 2.4_
    """
    assert validate_api_key("   ") is False
    assert validate_api_key("\t\n") is False
