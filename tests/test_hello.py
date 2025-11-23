from typer.testing import CliRunner

from denctl import app

runner = CliRunner()


def test_hello_default_name():
    """Test hello command with default name."""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello World!" in result.output


def test_hello_custom_name():
    """Test hello command with a custom name."""
    result = runner.invoke(app, ["hello", "Josh"])
    assert result.exit_code == 0
    assert "Hello Josh!" in result.output


def test_hello_with_special_characters():
    """Test hello command with special characters in name."""
    result = runner.invoke(app, ["hello", "wiscotrashpanda"])
    assert result.exit_code == 0
    assert "Hello wiscotrashpanda!" in result.output


def test_hello_help():
    """Test hello command help output."""
    result = runner.invoke(app, ["hello", "--help"])
    assert result.exit_code == 0
    assert "Say hello to someone." in result.output
    assert "NAME" in result.output


def test_app_help():
    """Test main app help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "denctl - raccoon's den automation CLI" in result.output
    assert "hello" in result.output
