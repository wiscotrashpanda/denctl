# Change: Add hello-again command

## Why
Add a second "hello world" style command to test the new OpenSpec format and provide an additional greeting command variant.

## What Changes
- Add new `hello-again` CLI command that outputs a greeting message
- Register the command in the main app alongside existing `hello` command

## Impact
- Affected specs: cli-commands (new capability)
- Affected code: `src/den/commands/hello.py`, `src/den/main.py`
