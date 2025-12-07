<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# den Codebase Guide for Agents

## Build, Lint, & Test

- **Install:** `uv pip install -e ".[dev]"` to install with dev dependencies.
- **Test:** Run all tests with `uv run pytest`.
- **Single Test:** `uv run pytest tests/test_hello.py::test_hello_default_output`
- **Lint:** Follow standard Python PEP 8. Type hints are required (mypy compatible).
- **Run:** `uv run den` or install via `uv pip install -e .` and run `den`.

## Code Style & Conventions

- **Imports:** Use absolute imports (e.g., `from den.commands.auth import auth_app`). Group: stdlib, 3rd-party, local.
- **Formatting:** Standard PEP 8. 2 spaces indentation.
- **Types:** Fully type-hinted functions/methods (args and return types).
- **Naming:** `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_CASE` for constants.
- **Docstrings:** Required for all public modules, functions, and classes. Use Google style (Summary, Args, Returns).
- **Structure:** Commands go in `src/den/commands/`. Main entry point is `src/den/main.py` using `typer`.
- **Error Handling:** Use custom exceptions where appropriate.
- **Testing:** Use `typer.testing.CliRunner` for CLI command tests.
