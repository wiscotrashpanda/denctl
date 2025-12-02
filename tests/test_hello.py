"""Unit tests for the hello command."""

from typer.testing import CliRunner

from den import __version__
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


def test_help_shows_available_commands():
  """Test that --help shows available commands including hello.

  Requirements: 5.4, 2.2
  """
  result = runner.invoke(app, ["--help"])
  assert result.exit_code == 0
  assert "hello" in result.output
  assert "Say hello to someone" in result.output


def test_version_displays_version_number():
  """Test that --version displays the version number.

  Requirements: 5.4, 2.4
  """
  result = runner.invoke(app, ["--version"])
  assert result.exit_code == 0
  assert __version__ in result.output
  assert "den version" in result.output


def test_hello_help_shows_name_option():
  """Test that hello --help shows the --name option.

  Requirements: 5.4, 2.3
  """
  result = runner.invoke(app, ["hello", "--help"])
  assert result.exit_code == 0
  assert "--name" in result.output
  assert "Name to greet" in result.output


def test_hello_again_default_output():
  """Test that den hello-again outputs 'Hello again, World!' by default."""
  result = runner.invoke(app, ["hello-again"])
  assert result.exit_code == 0
  assert "Hello again, World!" in result.output


def test_hello_again_custom_name():
  """Test that den hello-again --name outputs the custom name."""
  result = runner.invoke(app, ["hello-again", "--name", "Alice"])
  assert result.exit_code == 0
  assert "Hello again, Alice!" in result.output


def test_hello_again_appears_in_help():
  """Test that hello-again command appears in --help output."""
  result = runner.invoke(app, ["--help"])
  assert result.exit_code == 0
  assert "hello-again" in result.output
