## 1. Configuration

- [x] 1.1 Create `src/den/repo_config.py` with `get_default_org()` function following `launchctl_config.py` pattern
- [x] 1.2 Write tests for `repo_config.py` (config exists, missing, invalid JSON, missing key)

## 2. GitHub Repository Client

- [x] 2.1 Create `src/den/repo_client.py` with `RepoError` exception class
- [x] 2.2 Implement `repo_exists(org: str, name: str, token: str) -> bool` function
- [x] 2.3 Implement `create_repo(org: str, name: str, token: str) -> str` function returning clone URL
- [x] 2.4 Write tests for `repo_client.py` (create success, repo exists, API errors)

## 3. Repository Command

- [x] 3.1 Create `src/den/commands/repo.py` with `repo_app` Typer group
- [x] 3.2 Implement `create` command with `name` argument and `--org` option
- [x] 3.3 Add pre-flight check for existing GitHub repository
- [x] 3.4 Add pre-flight check for existing local directory at `~/Code/<name>`
- [x] 3.5 Add check for missing organization (no flag and no config)
- [x] 3.6 Add check for missing GitHub token
- [x] 3.7 Implement repository creation via `repo_client.create_repo()`
- [x] 3.8 Implement `git clone` to `~/Code/<name>` via subprocess
- [x] 3.9 Write tests for `repo.py` command (success path, all error scenarios)

## 4. Integration

- [x] 4.1 Register `repo_app` in `src/den/main.py`
- [x] 4.2 Run full test suite to ensure no regressions
