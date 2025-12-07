# repo-management Specification

## Purpose
TBD - created by archiving change add-repo-create-command. Update Purpose after archive.
## Requirements
### Requirement: Repository Creation Command

The system SHALL provide a `den repo create <name>` command that creates a GitHub repository in an organization and clones it to the local filesystem.

#### Scenario: Create repository with default organization

- **WHEN** user runs `den repo create my-project`
- **AND** `repo.default_org` is configured in `~/.config/den/config.json`
- **AND** repository `my-project` does not exist in the configured organization
- **AND** directory `~/Code/my-project` does not exist
- **THEN** a public GitHub repository is created in the configured organization
- **AND** the repository is cloned to `~/Code/my-project`
- **AND** a success message is displayed

#### Scenario: Create repository with explicit organization

- **WHEN** user runs `den repo create my-project --org other-org`
- **AND** repository `my-project` does not exist in `other-org`
- **AND** directory `~/Code/my-project` does not exist
- **THEN** a public GitHub repository is created in `other-org`
- **AND** the repository is cloned to `~/Code/my-project`
- **AND** a success message is displayed

#### Scenario: Repository already exists on GitHub

- **WHEN** user runs `den repo create my-project`
- **AND** repository `my-project` already exists in the target organization
- **THEN** no repository is created
- **AND** no local directory is created
- **AND** an error message is displayed indicating the repository already exists on GitHub

#### Scenario: Local directory already exists

- **WHEN** user runs `den repo create my-project`
- **AND** directory `~/Code/my-project` already exists
- **THEN** no repository is created on GitHub
- **AND** an error message is displayed indicating the local directory already exists

#### Scenario: No organization configured or specified

- **WHEN** user runs `den repo create my-project`
- **AND** no `--org` flag is provided
- **AND** `repo.default_org` is not configured
- **THEN** an error message is displayed indicating no organization is configured

### Requirement: Repository Configuration

The system SHALL support configuration of a default GitHub organization for repository creation.

#### Scenario: Read default organization from config

- **WHEN** `~/.config/den/config.json` contains `{"repo": {"default_org": "my-org"}}`
- **THEN** the `repo create` command uses `my-org` as the default organization

#### Scenario: Override default organization with flag

- **WHEN** `repo.default_org` is configured as `my-org`
- **AND** user provides `--org other-org` flag
- **THEN** the repository is created in `other-org` instead of `my-org`

### Requirement: GitHub Authentication

The system SHALL use the stored GitHub token for repository operations.

#### Scenario: Use stored GitHub token

- **WHEN** user runs `den repo create my-project`
- **AND** a GitHub token is stored via `den auth login`
- **THEN** the GitHub API calls use the stored token

#### Scenario: No GitHub token available

- **WHEN** user runs `den repo create my-project`
- **AND** no GitHub token is stored
- **THEN** an error message is displayed prompting user to run `den auth login`

