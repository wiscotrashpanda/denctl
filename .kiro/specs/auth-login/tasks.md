# Implementation Plan

- [x] 1. Create auth storage module
  - [x] 1.1 Implement auth storage functions
    - Create `src/den/auth_storage.py` with `get_auth_file_path()`, `load_credentials()`, `save_credentials()`, and `save_credential()` functions
    - Handle directory creation with `~/.config/den/` path
    - Implement JSON file reading/writing with proper error handling
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - [x] 1.2 Write property test for credential serialization round-trip
    - **Property 3: Credential serialization round-trip**
    - **Validates: Requirements 3.7**
  - [x] 1.3 Write property test for credential merge preservation
    - **Property 2: Credential merge preserves existing keys**
    - **Validates: Requirements 3.4**
  - [x] 1.4 Write property test for read/write consistency
    - **Property 4: Credential read/write consistency**
    - **Validates: Requirements 4.2, 4.3**
  - [x] 1.5 Git commit and push changes for auth storage module

- [x] 2. Create auth command module
  - [x] 2.1 Implement provider registry and validation
    - Create `src/den/commands/auth.py` with Provider dataclass and PROVIDERS registry
    - Add Anthropic as the initial provider with key_name "anthropic_api_key"
    - Implement API key validation function that rejects empty strings
    - _Requirements: 1.2, 2.3, 2.4, 4.1, 4.2_
  - [x] 2.2 Write property test for non-empty API key acceptance
    - **Property 1: Non-empty API key acceptance**
    - **Validates: Requirements 2.3**
  - [x] 2.3 Implement login command with provider selection and credential input
    - Create `login()` command function with Typer
    - Implement provider selection prompt using `typer.prompt()` with choices
    - Implement masked API key input using `typer.prompt(hide_input=True)`
    - Handle user cancellation gracefully
    - Display success message on completion
    - _Requirements: 1.1, 1.3, 1.4, 2.1, 2.2, 2.5, 3.6, 5.1, 5.2, 5.3, 5.4_
  - [x] 2.4 Git commit and push changes for auth command module

- [x] 3. Integrate auth command into main CLI
  - [x] 3.1 Register auth command group in main.py
    - Import auth_app from `den.commands.auth`
    - Add auth_app as a subcommand group using `app.add_typer()`
    - _Requirements: 1.1_
  - [x] 3.2 Git commit and push changes for CLI integration

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Add unit tests for auth functionality
  - [x] 5.1 Write unit tests for auth storage
    - Test `get_auth_file_path()` returns correct path
    - Test `load_credentials()` handles missing file
    - Test `save_credential()` creates directory if needed
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 5.2 Write unit tests for auth command
    - Test provider registry contains Anthropic
    - Test validation rejects empty strings
    - _Requirements: 1.2, 2.4_
  - [x] 5.3 Git commit and push changes for unit tests

- [x] 6. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
