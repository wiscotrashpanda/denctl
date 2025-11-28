"""Hash utility functions for content hashing."""

import hashlib


def compute_hash(content: str) -> str:
    """Compute SHA-256 hash of content.

    Args:
        content: The string content to hash.

    Returns:
        Hash as hex string with "sha256:" prefix.
    """
    hash_bytes = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return f"sha256:{hash_bytes}"
