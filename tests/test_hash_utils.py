"""Property-based tests for the hash utility module.

These tests use hypothesis to verify universal properties across all inputs.
"""

from hypothesis import given, settings, strategies as st

from den.hash_utils import compute_hash


@settings(max_examples=100)
@given(content=st.text())
def test_property_hash_computation_consistency(content: str):
    """**Feature: brew-backup, Property 1: Hash computation consistency**

    *For any* string content, computing the SHA-256 hash multiple times
    SHALL produce the same hash value.

    **Validates: Requirements 2.3**
    """
    hash1 = compute_hash(content)
    hash2 = compute_hash(content)

    assert hash1 == hash2


@settings(max_examples=100)
@given(content=st.text())
def test_property_hash_format_compliance(content: str):
    """Property test for hash format compliance.

    *For any* string content, the computed hash SHALL have the "sha256:" prefix
    followed by a valid hexadecimal string of 64 characters.
    """
    result = compute_hash(content)

    # Should have sha256: prefix
    assert result.startswith("sha256:")

    # Extract the hex part
    hex_part = result[7:]  # Remove "sha256:" prefix

    # Should be 64 hex characters (256 bits = 64 hex chars)
    assert len(hex_part) == 64

    # Should be valid hexadecimal
    assert all(c in "0123456789abcdef" for c in hex_part)
