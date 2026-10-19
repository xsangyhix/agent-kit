Labels: ready-for-agent
Status: awaiting-agent

## Description

Ship `0.1.0`. The version is already `0.1.0` in both `src/agent_kit/__init__.py` and `pyproject.toml`, so no bump is needed. What remains is the release itself: merge `agent/agent-kit` into `dev`, then tag `v0.1.0` on `dev`, as `docs/agents/project.md` prescribes.

This is a human step: the pre-commit hook refuses an agent session's commit on `dev`, and the user tags. The agent's role here is to confirm the release prerequisites are done, not to perform the merge.

## Blocked by

- agent-kit/25-choose-a-license
- agent-kit/26-version-note
- agent-kit/27-readme-install-paths

## Acceptance criteria

- [ ] Tickets 25, 26 and 27 are `done`.
- [ ] `agent/agent-kit` is merged into `dev` (all commits of the effort are reachable from `dev`).
- [ ] `v0.1.0` is tagged on `dev`.
- [ ] `agent-kit --version` reports `0.1.0`.

## Out of scope

- Bumping to a version other than `0.1.0`.
- Publishing to an index or announcing the release.
