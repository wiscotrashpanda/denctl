# Implementation Plan

- [x] 1. Update TaskConfig dataclass with environment_variables field
  - Add `environment_variables: dict[str, str] | None = None` field to
    TaskConfig
  - Update docstring to document the new field
  - _Requirements: 1.1, 1.2_

- [x] 2. Update generate_plist to include EnvironmentVariables
  - [x] 2.1 Add EnvironmentVariables dict to plist output when
    environment_variables is set and non-empty
    - Check if `config.environment_variables` is truthy (not None and not empty)
    - Add `EnvironmentVariables` key to plist_dict with the environment variables
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 2.2 Write property test for environment variables round-trip
    - **Property 1: Environment Variables Round-Trip Consistency**
    - **Validates: Requirements 1.1, 1.2, 1.4, 3.1, 3.2**
  - [x] 2.3 Write property test for empty environment variables omission
    - **Property 2: Empty Environment Variables Omission**
    - **Validates: Requirements 1.3**

- [x] 3. Update parse_plist to extract EnvironmentVariables
  - Extract `EnvironmentVariables` dict from plist if present
  - Set `environment_variables` field in returned TaskConfig
  - Handle missing key gracefully (set to None)
  - _Requirements: 1.4, 3.1_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Update launchctl install command to capture PATH
  - Import `os` module
  - Capture `os.environ.get("PATH")` before creating TaskConfig
  - Create environment_variables dict with PATH if available
  - Pass environment_variables to TaskConfig constructor
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 6. Write unit tests for environment variable handling
  - Test generate_plist with environment variables present
  - Test generate_plist with environment variables absent
  - Test parse_plist with EnvironmentVariables key present
  - Test parse_plist with EnvironmentVariables key absent
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 7. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
