# Agent Guidelines for Den

## Build & Test Commands
- **Install dev dependencies**: `uv pip install -e ".[dev]"`
- **Run all tests**: `uv run pytest`
- **Run single test file**: `uv run pytest tests/test_<module>.py`
- **Run single test function**: `uv run pytest tests/test_<module>.py::test_function_name`
- **Run tests in class**: `uv run pytest tests/test_<module>.py::TestClassName`
- **Build executable**: `pyinstaller den.spec`

## Code Style
- **Python version**: 3.12+
- **Module docstrings**: Triple-quoted strings at top of every module describing purpose
- **Function docstrings**: Google-style with Args, Returns, Raises sections
- **Type hints**: Required on all function signatures (e.g., `def foo(x: str) -> int:`)
- **Return types**: Use modern syntax (`dict[str, str]` not `Dict[str, str]`)
- **Imports**: Standard library, third-party, then local (grouped and sorted)
- **Error handling**: Create custom exceptions (e.g., `class GistError(Exception)`) for domain errors
- **File operations**: Use `pathlib.Path` not string paths
- **Test structure**: Group tests in classes (e.g., `class TestFormatBrewfile`)
- **Test naming**: Use descriptive names with underscores (e.g., `test_api_connection_error`)
- **Test docstrings**: Brief description of what is being tested
