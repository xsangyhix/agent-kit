# Changelog

All notable changes to the agent kit are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-19

### Added

- `agent-kit init` and `agent-kit update`: install the kit into a git project and
  move it to a newer version. A lock file records what was installed, so an update
  refuses to overwrite a project's own edits.
- The agent workflow, the local markdown issue tracker, the domain-docs layout, and
  the pre-commit guardrails, installed under `.agents/`.
- A snapshot of Matt Pocock's skill library, pinned to the commit recorded in
  `UPSTREAM`.

### License

- The kit's own files are MIT licensed; see LICENSE at the repository root.
- The vendored skills snapshot stays MIT licensed under Matt Pocock's own license.
