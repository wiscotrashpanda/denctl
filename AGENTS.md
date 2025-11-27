# AGENTS.md - Quick Reference for AI Coding Agents

## Build/Test Commands
- **Install:** `uv sync`
- **Test All:** `uv run pytest` or `uv run pytest tests/`
- **Single Test:** `uv run pytest tests/test_hello.py::test_hello_default_name`
- **Format:** `uv run ruff format .`
- **Lint:** `uv run ruff check .` (add `--fix` for auto-fix)
- **Type Check:** `uv run mypy .`
- **Run CLI:** `uv run den [command]`

## Code Style (Python 3.12+, Ruff, Mypy)
- **Type Hints:** Mandatory for all function signatures (args & returns)
- **Imports:** Standard lib → third-party → local. Ruff auto-sorts (I rule enabled)
- **Formatting:** Line-length 88, target py312 (ruff format)
- **Docstrings:** Google-style for modules, commands, complex functions
- **Output:** Use `rich.console.Console()`, NOT `print()`
- **Error Handling:** Raise `typer.Exit(code=N)` on errors, wrap subprocess calls in try/except
- **Config Files:** Store in `~/.config/den/`, use JSON, set 600 perms for secrets
- **Constants:** UPPER_CASE for module-level (CONFIG_DIR, PLIST_PATH, etc.)
- **CLI Commands:** Use `typer.Typer()` apps, register with `@app.command()`
