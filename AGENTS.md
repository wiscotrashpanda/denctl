# Agent Guidelines for denctl

## Commands
- **Install:** `uv sync` (installs dependencies & project in editable mode)
- **Test:** `uv run pytest`
- **Single Test:** `uv run pytest tests/path/to/test.py::test_function_name`
- **Format:** `uv run black .`
- **Run CLI:** `uv run denctl [command]`

## Code Style & Conventions
- **Language:** Python 3.14+. Use modern features.
- **Formatting:** Strictly follow `black` defaults.
- **Type Hints:** Mandatory for all function signatures (args & returns).
- **Imports:** Standard library first, then third-party, then local `denctl` imports.
- **Architecture:** `src` layout (`src/denctl/`). Keep `__init__.py` minimal.
- **CLI Framework:** Use `typer`. Define commands with `@app.command()`.
- **Testing:** Write `pytest` tests in `tests/`. Use `CliRunner` for integration tests.
- **Docstrings:** Clear docstrings for all commands and complex functions.
