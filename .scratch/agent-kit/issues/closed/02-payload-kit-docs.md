Status: done

## Description

**Where to work:** `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`. Source files are read from rc-machines (`D:\Marcin\PycharmProjects\rc-machines`, branch `agent/agent-kit` — not `dev`, because `GLOSSARY.md`'s `### Agent kit` terms exist only there). Ticket status changes go in rc-machines on `agent/agent-kit`.

Read `.scratch/agent-kit/design.md` (in rc-machines) first, sections 3, 4, 5 and 11. This ticket makes the kit's documents: the workflow docs become project-agnostic and move to their kit paths. **The rules themselves do not change** — only paths, project-specific content and rc-machines history citations.

Copy each file into the agent-kit repo, then edit the copy:

| rc-machines source | agent-kit destination |
| --- | --- |
| `docs/agents/workflow.md` | `src/agent_kit/payload/kit/workflow.md` |
| `docs/agents/issue-tracker.md` | `src/agent_kit/payload/kit/issue-tracker.md` |
| `docs/agents/triage-labels.md` | `src/agent_kit/payload/kit/triage-labels.md` |
| `docs/agents/domain.md` | `src/agent_kit/payload/kit/domain.md` |
| `GLOSSARY.md`, section `## Agent workflow` only (with its `###` subsections, including `### Agent kit`) | `src/agent_kit/payload/kit/GLOSSARY.md` |
| `docs/adr/0003-tracked-units.md` … `0006-guardrails.md` | `src/agent_kit/payload/kit/adr/` (same names) |
| `docs/adr/archived/0001-agent-workflow.md`, `0002-agent-workflow-v2.md` | `src/agent_kit/payload/kit/adr/archived/` (same names) |

Edits, applied to every copied file **except the two archived ADRs, which stay byte-for-byte** (they are historical records):

1. **Paths.** `docs/agents/workflow.md` → `.agents/kit/workflow.md`; same for `issue-tracker.md`, `triage-labels.md`, `domain.md`. `scripts/check_tracker.py` → `.agents/kit/check_tracker.py`. `scripts/hooks/pre-commit` / `scripts/hooks/` → `.agents/kit/hooks/pre-commit` / `.agents/kit/hooks/`. Workflow ADRs `docs/adr/000N-…` → `.agents/kit/adr/000N-…`; `docs/adr/archived/` (when it means the workflow ADRs) → `.agents/kit/adr/archived/`. Search each file for `docs/`, `scripts/` and `GLOSSARY.md` and decide each hit.
2. **Glossary references.** Where a doc says the workflow vocabulary is in `GLOSSARY.md`, say `.agents/kit/GLOSSARY.md`. The kit glossary opens with one paragraph: it holds the workflow terms; project terms live in the project's root `GLOSSARY.md`.
3. **Project-specific rules move out.** In `workflow.md` "Rules for the agent": rule 6 becomes "**Tests**: Test-Driven Development only. The project's test command is in `docs/agents/project.md`."; rules 7 and 8 (`src/server/public/`, `--allow-boot-update`) are deleted; add a rule "**Project rules**: `docs/agents/project.md` holds this project's own rules. Read it before your first edit." Renumber the rules. In the "Guardrails" section: the hook is `.agents/kit/hooks/pre-commit`; `agent-kit init` sets `core.hooksPath`; list the hook's checks as in design §11 (the release-build bullet is replaced by: "runs the project's local hook, `.agents/hooks.local/pre-commit`, last, if it exists"); a missing `harness.sh` is reported.
4. **rc-machines history citations removed.** Delete sentences that cite rc-machines events as evidence (for example "The issue-002 session is the evidence for this list…", "The close of ticket 02 (2026-10-16) is the evidence…", "Ticket 02's close on 2026-10-16 was recorded that way."). Keep the rule each one supported. Example paths in templates or prose that name rc-machines files (e.g. `src/shared/adapters/servo_adapter.py`, `front-loader`, `workflow-refactor`) become neutral examples (`src/app/module.py`, `my-feature`).
5. **`domain.md`** describes two ADR homes: project ADRs in `docs/adr/` (numbered on their own, never reusing a number), and the kit's workflow ADRs in `.agents/kit/adr/`, which a project never edits. Add the rule from design: a decision about the project is a project ADR; a decision that changes the workflow is a change to the agent kit, made in the agent-kit repo. Glossary: project terms in root `GLOSSARY.md`, workflow terms in `.agents/kit/GLOSSARY.md`.
6. **`issue-tracker.md`** keeps the local-markdown tracker, templates and overrides; only the edits above apply.

Then create `src/agent_kit/payload/agents-block.md`: the kit block content (design §5), without the marker lines. Use the current `AGENTS.md` of rc-machines as the model, with kit paths. It has: `## Rules` (English only; never commit on `dev`, agent work on `agent/<feature-slug>`, refused by the pre-commit hook), `## Agent skills` with `### Issue tracker`, `### Triage labels`, `### Domain docs`, `### Workflow`, `### Project rules` (`docs/agents/project.md`), `### Skill library` (`.agents/skills/`, Matt Pocock's library under MIT, see `.agents/skills/LICENSE` and `UPSTREAM`), and one opening sentence: "This block is managed by agent-kit and is replaced on `agent-kit update`; write project instructions outside the markers."

Delete `src/agent_kit/payload/README.txt` from ticket 01.

## Blocked by

- `agent-kit/01-kit-repo-skeleton`

## Acceptance criteria

- [x] Every file in the table exists at its destination; the archived ADRs are byte-identical to their sources.
- [x] `grep -rn "docs/agents\|scripts/\|src/server\|allow-boot-update\|front-loader\|issue-002\|ticket 02" src/agent_kit/payload/kit src/agent_kit/payload/agents-block.md` returns no hits, except mentions of `docs/agents/project.md` and anything inside `adr/archived/`.
- [x] Rule-by-rule, `payload/kit/workflow.md` has the same states, transitions and rules as rc-machines' `docs/agents/workflow.md`, apart from the changes listed in edit 3. List each rule you changed in the ticket's review summary.
- [x] `payload/agents-block.md` contains no marker lines and names only paths from design §4.
- [x] No file directly under `payload/` or `payload/kit/` starts with a dot.
- [x] The test suite still passes.

## Out of scope

- Any change to a workflow rule, state or label (design §13).
- The checker and hook (ticket 03), the skills (04), the project templates (05).
- Editing anything in rc-machines (ticket 09 does that).

## Questions

Grilling session recorded 2026-10-18, before implementation. All questions are answered; implementation started 2026-10-18.

**Q1 — How exactly does rule 6 (Tests) read?** The ticket says it *becomes* "**Tests**: Test-Driven Development only. The project's test command is in `docs/agents/project.md`." That drops the current generic clauses ("a failing test does not halt you…", "a ticket records any package-specific command it adds"). **Recommended:** exact replacement — the ticket is explicit, and losing a rule clause is a rule change beyond what the ticket already sanctions. **Answer:** accepted, 2026-10-18: exact replacement, no extra clauses.

**Q2 — Where does the new "Project rules" rule go?** Rules 7 and 8 are deleted and the new rule is added. **Recommended:** rule 7, right after Tests, pushing old 9–14 to 8–13: tests and project rules both answer "how do I work in this project", and the remaining rules read better after them. **Answer:** accepted, 2026-10-18.

**Q3 — Does workflow rule 10 name the location of a workflow ADR?** It says an architectural decision goes into `docs/adr/` and a change to the state machine needs a new ADR, but names no path for the latter. After the move that ADR belongs in `.agents/kit/adr/`. **Recommended:** amend its second sentence to "…needs a new ADR in `.agents/kit/adr/`" — a location clarification, not a new rule, keeping `workflow.md` self-consistent. **Answer:** accepted, 2026-10-18.

**Q4 — What shape does the kit glossary have?** **Recommended:** `# Glossary`, then the required one-paragraph opener ("This file holds the agent workflow's vocabulary. Project terms live in the project's root `GLOSSARY.md`."), then the copied `## Agent workflow` section with `### Agent kit`, `### States` and `### Review` verbatim, apart from the `docs/agents/workflow.md` reference inside "Follow-up". **Answer:** accepted, 2026-10-18.

**Q5 — Which neutral examples replace rc-machines' in `issue-tracker.md`?** The layout tree names `front-loader`, `workflow-refactor`, `issue-002` and servo tickets. **Recommended:** a `my-feature/` and `another-feature/` tree that keeps the retro-vs-issues and `closed/` distinctions visible, a slug-based filename scheme, and `src/app/module.py` for the path example (the ticket's own example). **Answer:** accepted, 2026-10-18.

**Q6 — What text goes in `agents-block.md`?** **Recommended:** the draft agreed during the session: no H1 and no markers; the opening sentence from the ticket; `## Rules`; `## Agent skills` with `### Issue tracker`, `### Triage labels`, `### Domain docs` (naming both glossary and ADR homes), `### Workflow`, `### Project rules` and `### Skill library` (naming `.agents/skills/LICENSE` and `.agents/skills/UPSTREAM`). **Answer:** accepted, 2026-10-18: use the agreed text verbatim.

**Q7 — Does this ticket add tests?** The ticket only says the suite still passes; tickets 05, 06 and 08 own payload tests. **Recommended:** no new tests — the acceptance checks are content checks done by grep in the review, and a second copy as a test would drift from the later packaging test. **Answer:** accepted, 2026-10-18.

**Q8 — "This repo" or "This project" in the copied docs?** The kit lands in a project that is a git repo, so "repo" stays true; changing it is cosmetic churn beyond path edits. **Recommended:** keep "repo". **Answer:** accepted, 2026-10-18.

**Q9 — What is the commit trail?** **Recommended:** mirror ticket 01 — rc-machines commits the answers plus `Status: in-progress` as `docs: record ticket 02 answers`; one content commit in agent-kit, `docs: add the kit workflow documents`, on `agent/agent-kit`; then rc-machines `docs: submit ticket 02 for review` with the review summary, changed-rule list and verification table. No push. **Answer:** accepted, 2026-10-18.

## Review

Implementation complete, submitted for review.

### Summary of changes

- `D:\Marcin\PycharmProjects\agent-kit` — one content commit on `agent/agent-kit`, `docs: add the kit workflow documents` (`4ed1e0f`). `dev` and `main` are unchanged at `b5ff54d`.
- `src/agent_kit/payload/kit/` — `workflow.md`, `issue-tracker.md`, `triage-labels.md`, `domain.md`, `GLOSSARY.md`, `adr/0003-tracked-units.md` … `0006-guardrails.md`, `adr/archived/0001-agent-workflow.md` and `0002-agent-workflow-v2.md`.
- `src/agent_kit/payload/agents-block.md` — the kit block content, without marker lines.
- `src/agent_kit/payload/README.txt` — deleted (the ticket-01 placeholder).
- This ticket — the Questions, status and acceptance criteria.

### Changed workflow rules

States and transitions are identical to rc-machines' file. The rule changes are:

| Change | Rule (kit file) |
| --- | --- |
| Replaced with the ticket's sentence; the rc-machines test command and its package-specific clauses removed | 6 **Tests** |
| Deleted: `src/server/public/` and `--allow-boot-update` | old 7, 8 |
| Added: **Project rules** (`docs/agents/project.md`) | new 7 |
| Renumbered, wording unchanged: old 9–14 → 8–13 | 8–13 |
| Added "in `.agents/kit/adr/`" to the second sentence (Q3) | old 10 → 9 |
| Neutral example path: `src/shared/adapters/servo_adapter.py` → `src/app/module.py` | old 13 → 12 |
| Removed the ticket-02-close evidence sentence; the rule itself unchanged | 3 |

Outside the rules: "Definition of ready" lost the rc-machines noun ("machines" → "components"); the Guardrails section was rewritten to the kit hook path, `agent-kit init` setting `core.hooksPath`, the `.agents/kit/harness.sh` markers, `.agents/kit/check_tracker.py`, the local hook bullet replacing the release-build bullet, and the missing-`harness.sh` bullet. All other changes are paths, glossary references and citations.

### Verification

| Check | Result |
| --- | --- |
| Archived ADRs vs `git show HEAD:docs/adr/archived/<name>` | byte-identical (1087 and 3399 bytes, no CR) |
| Acceptance grep over `payload/kit` and `agents-block.md` | 9 hits: all `docs/agents/project.md` or inside `adr/archived/` |
| `workflow.md` diff vs rc-machines source | only the changes listed above |
| `agents-block.md` marker lines | none |
| Dot-files directly under `payload/` or `payload/kit/` | none |
| `py -3.14 -m unittest discover -s tests -t . -v` | 4 tests, OK |
| `git diff dev...HEAD --check` | clean |
| `git -C agent-kit branch -vv` | `agent/agent-kit` at `4ed1e0f`; `dev` and `main` at `b5ff54d` |

### Notes for the reviewer

1. **Q3 and Q6 choices.** Rule 9 names `.agents/kit/adr/` for a workflow ADR, and the block uses the agreed text verbatim, including "which opencode discovers there". opencode is the only harness today (design §13); the block is static, so a second harness will need that sentence revisited.
2. **Pre-submission review.** A two-axis review of `git diff HEAD~1...HEAD` ran. It found no missing ticket requirement. Four prose/findings were fixed: "machines" → "components"; the harness bullet now says "variables named in `.agents/kit/harness.sh`"; `domain.md` names both ADR homes as the shape reference and says "workflow ADR 0006". Four judgement calls were left as they are: rule 8's `GLOSSARY.md` refers to the project glossary (workflow terms are kit-owned; `domain.md` consumer rule 5 carries the split); the block naming `.scratch/<feature>/issues/` is allowed by acceptance criterion 4 (design §4) and by Q6; `workflow.md` says `agent-kit init` sets `core.hooksPath` as edit 3 words it (design §9 also has update re-set it); the state→label pairings still appear in both `workflow.md` and `triage-labels.md`, as in the source.
3. **No new tests (Q7).** The payload checks are content checks; tickets 05, 06 and 08 add the executable ones.
4. **No push, no remote.** The user pushes and merges.
