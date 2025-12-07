# Design: Add repo create command

## Context

The `den` CLI already has patterns for:
- Configuration via `~/.config/den/config.json` (see `launchctl_config.py`)
- GitHub API interaction using `httpx` (see `gist_client.py`)
- Credential storage via `auth_storage.py` with existing `github_token` support

This change follows established patterns while adding repository management.

## Goals / Non-Goals

**Goals:**
- Automate GitHub repo creation + local clone in one command
- Support organization-level repository creation
- Fail fast if repo or directory already exists

**Non-Goals:**
- Personal (non-org) repository creation
- Repository deletion or management
- Custom repository templates or settings

## Decisions

### Configuration Structure

**Decision:** Add `repo.default_org` to existing config.json structure.

```json
{
  "launchctl": { "domain": "com.example" },
  "repo": { "default_org": "my-org" }
}
```

**Rationale:** Follows the existing nested config pattern from `launchctl_config.py`.

### GitHub API Client

**Decision:** Create `repo_client.py` similar to `gist_client.py`.

**Rationale:** Maintains separation of concerns and follows existing patterns. Uses the same `httpx` library and error handling approach.

### Local Directory Path

**Decision:** Hardcode `~/Code` as the base directory.

**Rationale:** Keeps initial implementation simple. Can be made configurable later if needed.

### Clone Method

**Decision:** Use `git clone` via subprocess rather than a Python git library.

**Rationale:** 
- Avoids adding `GitPython` dependency
- Git is already installed on target systems (macOS)
- Simple and reliable for this use case

### Pre-flight Checks

**Decision:** Check both GitHub repo existence and local directory existence before any mutations.

**Rationale:** Fail fast with clear error messages. User must explicitly clean up before retrying.

## Risks / Trade-offs

- **Risk:** Git not installed → Mitigation: Assume git is available (reasonable for dev machines)
- **Risk:** Network failure during clone after repo created → Mitigation: User can manually clone; repo exists and is recoverable
- **Trade-off:** Hardcoded `~/Code` path is inflexible but keeps implementation simple

## Open Questions

None - all requirements clarified by user.
