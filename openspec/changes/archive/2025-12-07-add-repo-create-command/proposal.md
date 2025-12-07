# Change: Add repo create command

## Why

Creating a new project requires multiple manual steps: creating a GitHub repository, cloning it locally, and organizing it in the correct directory. This command automates the workflow by creating a GitHub repository in a configured organization and cloning it to `~/Code/<name>` in one step.

## What Changes

- Add new `den repo create <name>` command with optional `--org` flag
- Add `repo.default_org` configuration option in `~/.config/den/config.json`
- Create new `repo` command group with `create` subcommand
- Create GitHub repository via API (public by default)
- Clone the new repository to `~/Code/<name>`
- Pre-flight checks to prevent conflicts with existing repos or directories

## Impact

- Affected specs: New `repo-management` capability
- Affected code:
  - `src/den/commands/repo.py` (new)
  - `src/den/repo_client.py` (new) - GitHub repository API client
  - `src/den/repo_config.py` (new) - Configuration for default org
  - `src/den/main.py` - Register repo command group
  - Uses existing `auth_storage.py` for GitHub token
