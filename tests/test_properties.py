"""Property-based tests for the den CLI application.

These tests use hypothesis to verify universal properties across all inputs.
"""

from hypothesis import given, settings, strategies as st
from typer.testing import CliRunner

from den.main import app

runner = CliRunner()


@settings(max_examples=100)
@given(name=st.text(min_size=1, alphabet=st.characters(blacklist_categories=("Cs",))))
def test_property_name_greeting_format_consistency(name: str):
    """**Feature: den-cli, Property 1: Name greeting format consistency**

    *For any* valid name string provided to the hello command, the output
    SHALL contain the exact format "Hello, {name}!" where {name} is the
    provided input.

    **Validates: Requirements 3.2**
    """
    result = runner.invoke(app, ["hello", "--name", name])
    expected = f"Hello, {name}!"
    assert expected in result.output


@settings(max_examples=100)
@given(name=st.text(min_size=1, alphabet=st.characters(blacklist_categories=("Cs",))))
def test_property_successful_exit_code(name: str):
    """**Feature: den-cli, Property 2: Successful execution exit code**

    *For any* valid invocation of the hello command (with or without the
    --name option), the command SHALL return exit code 0.

    **Validates: Requirements 3.4**
    """
    result = runner.invoke(app, ["hello", "--name", name])
    assert result.exit_code == 0
