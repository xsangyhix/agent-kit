<!-- agent-kit:begin -->
This block is managed by agent-kit and is replaced on `agent-kit update`; write project instructions outside the markers.

## Rules

- **English only.** Replies, commit messages and issue files are all written in English.
- **Never commit on `dev`.** Agent work happens on `agent/<feature-slug>`; a pre-commit hook refuses an agent session's commit on `dev`.

## Agent skills

### Issue tracker

Issues are tracked as local markdown files under `.scratch/<feature>/issues/`. See `.agents/kit/issue-tracker.md`.

### Triage labels

The five canonical triage roles use their default label strings. See `.agents/kit/triage-labels.md`.

### Domain docs

Single-context layout: one `GLOSSARY.md` and `docs/adr/` at the repo root for project terms and decisions; the workflow's terms are in `.agents/kit/GLOSSARY.md` and its decisions in `.agents/kit/adr/`. See `.agents/kit/domain.md`.

### Workflow

Issues move through a state machine from `draft` to `done`. See `.agents/kit/workflow.md`.

### Project rules

This project's own rules are in `docs/agents/project.md`. Read it before your first edit.

### Skill library

The skill library lives in `.agents/skills/`, which opencode discovers there. It is Matt Pocock's library, under MIT, unmodified: see `.agents/skills/LICENSE` and `.agents/skills/UPSTREAM`.
<!-- agent-kit:end -->

## Project

agent-kit: the project-agnostic agent setup (workflow docs, guardrails, skill library) and the `agent-kit` tool that installs it into projects. Project rules: `docs/agents/project.md`.
