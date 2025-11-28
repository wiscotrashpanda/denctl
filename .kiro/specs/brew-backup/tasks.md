# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Add `anthropic` and `httpx` to project dependencies in `pyproject.toml`
  - Create placeholder files for new modules
  - Git commit and push changes
  - _Requirements: 3.1, 4.1_

- [x] 2. Implement hash utility module
  - [x] 2.1 Create `src/den/hash_utils.py` with `compute_hash()` function
    - Implement SHA-256 hash computation for string content
    - Return hash as hex string with "sha256:" prefix
    - _Requirements: 2.3_
  - [x] 2.2 Write property test for hash consistency
    - **Property 1: Hash computation consistency**
    - **Validates: Requirements 2.3**
  - [x] 2.3 Git commit and push hash utility module
    - Commit implementation and tests
    - Push to remote repository

- [x] 3. Implement state storage module
  - [x] 3.1 Create `src/den/state_storage.py` with state management functions
    - Implement `get_state_file_path()` returning `~/.config/den/state.json`
    - Implement `load_state()` to read existing state
    - Implement `save_state()` to write state, merging with existing content
    - Implement `get_brew_state()` to retrieve brew-specific state
    - Implement `save_brew_state()` to save hash and gist_id under "brew" key
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  - [x] 3.2 Write property test for state merge preservation
    - **Property 2: State merge preserves existing keys**
    - **Validates: Requirements 5.3**
  - [x] 3.3 Write property test for state serialization round-trip
    - **Property 3: State serialization round-trip**
    - **Validates: Requirements 5.6**
  - [x] 3.4 Git commit and push state storage module
    - Commit implementation and tests
    - Push to remote repository

- [x] 4. Implement brew logger module
  - [x] 4.1 Create `src/den/brew_logger.py` with logging configuration
    - Implement `get_log_file_path()` returning `~/.config/den/logs/brew-upgrade.log`
    - Implement `setup_brew_logger()` to configure file handler with timestamp and level format
    - Create log directory if it doesn't exist
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [x] 4.2 Write property test for log entry format
    - **Property 4: Log entry format compliance**
    - **Validates: Requirements 6.3, 6.4**
  - [x] 4.3 Git commit and push brew logger module
    - Commit implementation and tests
    - Push to remote repository

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement brew runner module
  - [x] 6.1 Create `src/den/brew_runner.py` with Homebrew command execution
    - Implement `run_brew_upgrade()` to execute `brew upgrade`
    - Implement `generate_brewfile()` to execute `brew bundle dump --force --stdout`
    - Handle subprocess errors and return appropriate exceptions
    - _Requirements: 1.1, 1.4, 2.1_
  - [x] 6.2 Write unit tests for brew runner
    - Test successful command execution (mocked)
    - Test error handling for failed commands
    - _Requirements: 1.1, 1.4, 2.1_
  - [x] 6.3 Git commit and push brew runner module
    - Commit implementation and tests
    - Push to remote repository

- [x] 7. Implement GitHub Gist client module
  - [x] 7.1 Create `src/den/gist_client.py` with Gist API operations
    - Implement `create_gist()` to create new Gist, returning (gist_id, gist_url)
    - Implement `update_gist()` to update existing Gist, returning gist_url
    - Use httpx for HTTP requests to GitHub API
    - Handle API errors with descriptive exceptions
    - _Requirements: 4.1, 4.2, 4.5, 4.7_
  - [x] 7.2 Write unit tests for Gist client
    - Test Gist creation (mocked API)
    - Test Gist update (mocked API)
    - Test error handling for API failures
    - _Requirements: 4.1, 4.2, 4.7_
  - [x] 7.3 Git commit and push Gist client module
    - Commit implementation and tests
    - Push to remote repository

- [x] 8. Implement Brewfile formatter module
  - [x] 8.1 Create `src/den/brewfile_formatter.py` with Anthropic integration
    - Implement `build_formatting_prompt()` to construct the prompt
    - Implement `format_brewfile()` to call Anthropic API and return formatted content
    - Include instructions for header, descriptions, and categorization in prompt
    - Handle API errors with descriptive exceptions
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.7_
  - [x] 8.2 Write unit tests for Brewfile formatter
    - Test prompt construction includes required instructions
    - Test API call handling (mocked)
    - Test error handling for API failures
    - _Requirements: 3.1, 3.3, 3.4, 3.5, 3.7_
  - [x] 8.3 Git commit and push Brewfile formatter module
    - Commit implementation and tests
    - Push to remote repository

- [x] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement brew upgrade command
  - [x] 10.1 Create `src/den/commands/brew.py` with upgrade command
    - Create `brew_app` Typer group
    - Implement `upgrade()` command orchestrating the full workflow
    - Display progress messages for each step
    - Handle hash comparison to skip unchanged Brewfiles
    - Load API keys from auth storage
    - Handle missing credentials with helpful error messages
    - _Requirements: 1.2, 1.3, 2.2, 2.4, 2.5, 3.2, 3.6, 4.3, 4.4, 4.6, 7.1, 7.2, 7.3_
  - [x] 10.2 Register brew command in main.py
    - Import and add `brew_app` to main application
    - _Requirements: 1.1_
  - [x] 10.3 Write integration tests for brew upgrade command
    - Test full workflow with mocked external services
    - Test skip behavior when Brewfile unchanged
    - Test error handling for missing credentials
    - _Requirements: 1.2, 2.4, 3.6, 4.6_
  - [x] 10.4 Git commit and push brew upgrade command
    - Commit implementation and tests
    - Push to remote repository

- [x] 11. Add GitHub provider to auth login
  - [x] 11.1 Update `src/den/commands/auth.py` to include GitHub provider
    - Add GitHub provider to PROVIDERS dictionary
    - Use key name "github_token" for storage
    - _Requirements: 4.6_
  - [x] 11.2 Git commit and push GitHub provider update
    - Commit changes to auth.py
    - Push to remote repository

- [x] 12. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Update Brewfile formatting prompt style
  - [x] 13.1 Update `build_formatting_prompt()` in `src/den/brewfile_formatter.py`
    - Change prompt to use inline comments at end of each line (e.g., `brew "git"  # Distributed version control`)
    - Add decorated section headers with `# ============` separators
    - Update header to note file was generated by `den` with `brew bundle` and `brew bundle cleanup` usage instructions
    - _Requirements: 3.3, 3.4, 3.5_
  - [x] 13.2 Update unit tests for new prompt format
    - Verify prompt includes inline comment instruction
    - Verify prompt includes decorated section header instruction
    - Verify prompt includes den generation header instruction
    - _Requirements: 3.3, 3.4, 3.5_

- [x] 14. Add --force option to upgrade command
  - [x] 14.1 Update `upgrade()` command in `src/den/commands/brew.py`
    - Add `--force` / `-f` option using Typer
    - Modify hash comparison logic to skip check when force is True
    - _Requirements: 2.4, 2.6_
  - [x] 14.2 Update integration tests for --force option
    - Test that --force bypasses hash check
    - Test that --force proceeds with formatting and backup
    - _Requirements: 2.6_

- [x] 15. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
