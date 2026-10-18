Status: done

## Description

**Where to work:** `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`. Ticket status changes go in rc-machines (`D:\Marcin\PycharmProjects\rc-machines`) on `agent/agent-kit`.

Read `.scratch/agent-kit/design.md` (in rc-machines) sections 4 and 5 first. This ticket writes the starters `agent-kit init` puts into a new project when the file is missing. They are project-owned: after init, the project edits them freely and the kit never touches them again (except the kit block in `AGENTS.md`).

Create in `src/agent_kit/payload/templates/`:

1. `AGENTS.md`:
   ```
   <!-- agent-kit:begin -->
   {{KIT_BLOCK}}
   <!-- agent-kit:end -->

   ## Project

   <What this project is, in two or three sentences. Project rules live in `docs/agents/project.md`.>
   ```
   `{{KIT_BLOCK}}` is the literal placeholder ticket 06 replaces with `payload/agents-block.md`. Nothing else in the template uses `{{…}}`.
2. `GLOSSARY.md`: a `# Glossary` title; one paragraph: "Canonical vocabulary for this project. Skills read this file first and use its terms verbatim. If a term is missing, propose adding it here rather than inventing a synonym. The agent workflow's own terms are in `.agents/kit/GLOSSARY.md`."; then an empty `## Terms` section with one commented example line in the format `- **Term** — definition. _Avoid_: synonyms.`
3. `docs/agents/project.md`: a `# Project rules` title; one paragraph saying this file holds the rules specific to this project and is read by agents before their first edit (rule in `.agents/kit/workflow.md`); then these sections, each with a one-line placeholder in angle brackets:
   - `## Tests` — the command that runs the whole test suite.
   - `## Do not edit` — generated or protected paths.
   - `## Release` — anything the local hook (`.agents/hooks.local/pre-commit`) does, if one exists.
   - `## ADR numbering` — "Project ADRs in `docs/adr/` start at `0001` unless stated otherwise here."
   - `## Other rules`

Write a test `tests/test_templates.py` that checks: each template exists; `AGENTS.md` has exactly one begin marker, one end marker, begin before end, and `{{KIT_BLOCK}}` between them; no template contains `rc-machines`, `src/server`, `front-loader` or `servo`.

## Blocked by

- `agent-kit/02-payload-kit-docs` — the templates point at the doc paths that ticket fixes.

## Acceptance criteria

- [x] The three templates exist with the content above.
- [x] `tests/test_templates.py` passes, and so does the whole suite.
- [x] Every path a template names exists in design §4.

## Out of scope

- The code that installs the templates (ticket 06).
- rc-machines' own `docs/agents/project.md` (ticket 09).

## Review

Implementation complete, submitted for review.

### Summary of changes

- `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`: one commit, `249bfc3` — `feat: add project starter templates`.
  - `src/agent_kit/payload/templates/AGENTS.md` — the marker pair around `{{KIT_BLOCK}}`, then the `## Project` section.
  - `src/agent_kit/payload/templates/GLOSSARY.md` — the opener paragraph, an empty `## Terms`, and one commented example line.
  - `src/agent_kit/payload/templates/docs/agents/project.md` — the five sections; `## ADR numbering` carries the required sentence, the rest carry angle-bracket placeholders.
  - `tests/test_templates.py` — six tests covering the required checks, plus: `{{KIT_BLOCK}}` occurs once, and no other template uses `{{…}}`.
- This ticket — status and label moved for review, acceptance criteria ticked.

### Verification

| Check | Result |
| --- | --- |
| `py -3.14 -m unittest tests.test_templates -v` (red before the templates, green after) | 6 tests, OK |
| `py -3.14 -m unittest discover -s tests -t . -v` | 43 tests, OK, exit 0 |
| Paths named in the templates vs design §4 | `.agents/kit/GLOSSARY.md`, `.agents/kit/workflow.md`, `docs/agents/project.md`, `.agents/hooks.local/pre-commit`, `docs/adr/` — all in §4; asserted by a test |
| Forbidden terms (`rc-machines`, `src/server`, `front-loader`, `servo`) | none; asserted by a test |
| Template line endings | LF, trailing newline |
| `git diff --check` / `git diff --cached --check` | clean |
| `git -C agent-kit branch -vv` | `agent/agent-kit` at `249bfc3`; `dev` and `main` at `b5ff54d` |

### Notes for the reviewer

1. **`{{KIT_BLOCK}}` is inside the markers on its own line.** Ticket 06 replaces the placeholder with the content of `payload/agents-block.md`; a test pins that it is the only placeholder among the templates.
2. **The path test is an allowlist from design §4.** It extracts every backticked path from the templates and requires it to match or sit under a §4 location. A future template that legitimately names a new path will need the list in `tests/test_templates.py` updated with §4.
3. **`## ADR numbering` is not an angle-bracket placeholder.** The ticket supplied the exact sentence for that section, so it is written verbatim; the four other sections use placeholders.
4. **`docs/agents/project.md`'s opener cites rule 7.** It points at `.agents/kit/workflow.md`, whose rule 7 is the "read it before your first edit" rule.
