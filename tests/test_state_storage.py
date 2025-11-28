"""Property-based tests for state storage module.

These tests use hypothesis to verify universal properties for state persistence.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from hypothesis import given, settings, strategies as st

from den.state_storage import (
    load_state,
    save_state,
    get_brew_state,
    save_brew_state,
)


# Strategy for generating valid JSON-serializable state dictionaries
json_primitives = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(),
)

json_values = st.recursive(
    json_primitives,
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(min_size=1, max_size=10), children, max_size=5),
    ),
    max_leaves=10,
)

# Strategy for state dictionaries (string keys, JSON-serializable values)
state_dict_strategy = st.dictionaries(
    st.text(
        min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=("Cs",))
    ),
    json_values,
    max_size=5,
)


@settings(max_examples=100)
@given(
    existing_state=state_dict_strategy,
    new_state=state_dict_strategy,
)
def test_property_state_merge_preserves_existing_keys(
    existing_state: dict, new_state: dict
) -> None:
    """**Feature: brew-backup, Property 2: State merge preserves existing keys**

    *For any* existing state.json content and any new brew state being saved,
    the save operation SHALL preserve all existing keys while adding or updating
    the "brew" key.

    **Validates: Requirements 5.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state.json"

        with patch("den.state_storage.get_state_file_path", return_value=state_file):
            # Write existing state directly to file
            if existing_state:
                state_file.parent.mkdir(parents=True, exist_ok=True)
                with state_file.open("w", encoding="utf-8") as f:
                    json.dump(existing_state, f)

            # Save new state (which should merge)
            save_state(new_state)

            # Load the result
            result = load_state()

            # All keys from existing state that are not in new_state should be preserved
            for key in existing_state:
                if key not in new_state:
                    assert key in result, f"Key '{key}' was not preserved"
                    assert result[key] == existing_state[key], (
                        f"Value for key '{key}' was modified"
                    )

            # All keys from new_state should be present with new values
            for key in new_state:
                assert key in result, f"New key '{key}' was not added"
                assert result[key] == new_state[key], (
                    f"Value for new key '{key}' is incorrect"
                )


@settings(max_examples=100)
@given(
    brewfile_hash=st.text(min_size=1, max_size=100),
    gist_id=st.text(min_size=1, max_size=100),
)
def test_property_state_serialization_round_trip(
    brewfile_hash: str, gist_id: str
) -> None:
    """**Feature: brew-backup, Property 3: State serialization round-trip**

    *For any* valid brew state dictionary, serializing to JSON and deserializing
    back SHALL produce an equivalent dictionary.

    **Validates: Requirements 5.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "state.json"

        with patch("den.state_storage.get_state_file_path", return_value=state_file):
            # Save brew state
            save_brew_state(brewfile_hash, gist_id)

            # Load it back
            result = get_brew_state()

            # Verify round-trip produces equivalent values
            assert result is not None, "Brew state should exist after saving"
            assert result["brewfile_hash"] == brewfile_hash, (
                "brewfile_hash should round-trip correctly"
            )
            assert result["gist_id"] == gist_id, "gist_id should round-trip correctly"
