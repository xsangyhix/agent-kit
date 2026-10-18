# 0001 — Agent workflow

- **Status**: superseded by ADR-0002
- **Context**: Agents need a repeatable way to pick up an issue, clarify it, implement it, and get it reviewed. Without an explicit workflow, each task risks being handled differently, and there is no shared vocabulary for where a task stands.
- **Decision**: Adopt a state-machine workflow documented in `docs/agents/workflow.md`. Issues live as markdown files under `.scratch/<feature>/`. States are `draft`, `questioning`, `ready`, `in-progress`, `in-review`, `changes-requested`, `done`, mapped onto the existing triage labels. The agent works on `agent/<issue-id>-<slug>` branches off `dev`, never touches `dev`, follows TDD, and submits work for review via comments in the issue file. Approved issues are moved to `.scratch/<feature>/done/`.
- **Consequences**: The workflow is versioned; changes require a new ADR that supersedes this one. The triage labels remain the single labelling scheme. Review is lightweight (comments in the issue file) and leaves a written trail. The agent cannot merge or push on its own.
