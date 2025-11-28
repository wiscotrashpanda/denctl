"""Unit tests for the hello command."""

from typer.testing import CliRunner

from den.main import app

runner = CliRunner()


def test_hello_default_output():
    """Test that den hello outputs 'Hello, World!' by default."""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output


def test_hello_custom_name():
    """Test that den hello --name outputs the custom name."""
    result = runner.invoke(app, ["hello", "--name", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.output


def test_hello_exit_code_success():
    """Test that hello command returns exit code 0 on success."""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
