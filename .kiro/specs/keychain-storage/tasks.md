# Implementation Plan

- [ ] 1. Add keyring dependency and create backend protocol
  - [x] 1.1 Add keyring to project dependencies in pyproject.toml
    - Add `keyring>=24.0.0` to the dependencies list
    - _Requirements: 1.1_
  - [x] 1.2 Create KeychainBackend protocol and InMemoryBackend for testing
    - Create `src/den/keychain_backend.py` with Protocol definition
    - Implement `InMemoryBackend` class for testing
    - _Requirements: 5.1, 5.2_

- [ ] 2. Implement MacOSKeychainBackend
  - [ ] 2.1 Create MacOSKeychainBackend class using keyring library
    - Implement `get_credential`, `set_credential`, `delete_credential`, `list_credentials`
    - Use service name "den-cli" for all operations
    - Implement credential registry for listing credentials
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [ ] 2.2 Write property test for credential round-trip
    - **Property 1: Credential Round-Trip Consistency**
    - **Validates: Requirements 1.1, 1.2**
  - [ ] 2.3 Write property test for delete removes credential
    - **Property 2: Delete Removes Credential**
    - **Validates: Requirements 1.3**

- [ ] 3. Refactor auth_storage to use backend abstraction
  - [ ] 3.1 Update auth_storage.py to use KeychainBackend
    - Add backend injection via `set_backend()` function
    - Default to `MacOSKeychainBackend` in production
    - Maintain existing function signatures for backward compatibility
    - _Requirements: 2.1, 2.2, 2.3_
  - [ ] 3.2 Write property test for bulk save and load
    - **Property 3: Bulk Save and Load Consistency**
    - **Validates: Requirements 2.2, 2.3**

- [ ] 4. Implement error handling
  - [ ] 4.1 Create KeychainAccessError exception class
    - Add to `src/den/keychain_backend.py`
    - Include original error and guidance message
    - _Requirements: 3.1, 3.3_
  - [ ] 4.2 Add error handling to MacOSKeychainBackend
    - Wrap keyring exceptions in KeychainAccessError
    - Return None for missing credentials (not an error)
    - _Requirements: 3.1, 3.2, 3.3_

- [ ] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement migration from auth.json
  - [ ] 6.1 Create migration module
    - Create `src/den/auth_migration.py`
    - Implement `migrate_from_json()` function
    - Implement `get_legacy_auth_file_path()` function
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [ ] 6.2 Write property test for migration transfers and cleans up
    - **Property 4: Migration Transfers and Cleans Up**
    - **Validates: Requirements 4.1, 4.2**
  - [ ] 6.3 Write property test for migration preserves existing credentials
    - **Property 5: Migration Preserves Existing Keychain Credentials**
    - **Validates: Requirements 4.4**

- [ ] 7. Integrate migration into application startup
  - [ ] 7.1 Add migration call to auth_storage initialization
    - Call `migrate_from_json()` when module loads
    - Handle migration errors gracefully with logging
    - _Requirements: 4.1, 4.3_

- [ ] 8. Update existing tests
  - [ ] 8.1 Update test_auth_storage.py to use InMemoryBackend
    - Inject InMemoryBackend in test setup
    - Ensure existing tests pass with new implementation
    - _Requirements: 5.1, 5.2_

- [ ] 9. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
