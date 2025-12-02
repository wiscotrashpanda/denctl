## ADDED Requirements

### Requirement: Hello Again Command
The CLI SHALL provide a `hello-again` command that outputs a greeting message to the console.

#### Scenario: Default greeting output
- **WHEN** user runs `den hello-again` without arguments
- **THEN** the output SHALL be "Hello again, World!"

#### Scenario: Custom name greeting
- **WHEN** user runs `den hello-again --name Alice`
- **THEN** the output SHALL be "Hello again, Alice!"

#### Scenario: Command appears in help
- **WHEN** user runs `den --help`
- **THEN** the `hello-again` command SHALL be listed in available commands
