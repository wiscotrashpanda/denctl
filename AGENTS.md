# Agent Guidelines for denctl

## Commands
- **Install:** `uv sync` (installs dependencies & project in editable mode)
- **Test:** `uv run pytest` or `uv run pytest tests/`
- **Single Test:** `uv run pytest tests/test_hello.py::test_hello_default_name`
- **Format:** `uv run ruff format .`
- **Lint:** `uv run ruff check .` or `uv run ruff check . --fix` (auto-fix)
- **Type Check:** `uv run mypy .`
- **Run CLI:** `uv run denctl [command]` or `uv run den [command]`

## Code Style & Conventions
- **Language:** Python 3.12+ (pyproject.toml requires >=3.12)
- **Formatting:** Use `ruff` (line-length=88, target py312)
- **Linting:** Ruff with E, F, I, B rules (Pyflakes, pycodestyle, isort, flake8-bugbear)
- **Type Hints:** Mandatory for all function signatures (args & returns). Use `typing` imports.
- **Imports:** Standard library first, then third-party, then local `denctl` imports (ruff auto-sorts)
- **Architecture:** `src` layout (`src/denctl/`). Keep `__init__.py` minimal (version only).
- **CLI Framework:** Use `typer` with `typer.Typer()` apps. Commands via `@app.command()`.
- **Output:** Use `rich.console.Console()` for styled terminal output, not raw `print()`.
- **Testing:** Write `pytest` tests in `tests/`. Use `typer.testing.CliRunner` for CLI tests.
- **Docstrings:** Google-style docstrings for all modules, commands, and complex functions.
- **Error Handling:** Raise `typer.Exit(code=N)` on errors, use rich console for messages.
- **Config Files:** Store in `~/.config/denctl/`, use JSON, set 600 permissions for secrets.
- **Subprocess:** Use `subprocess.run()` with `capture_output=True`, `text=True`, `check=True` where appropriate.
- **Constants:** Use UPPER_CASE for module-level constants (CONFIG_DIR, PLIST_PATH, etc.).
