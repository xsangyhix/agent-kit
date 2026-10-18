Status: done

## Description

**Where to work:** both repos, each on its `agent/agent-kit` branch: `D:\Marcin\PycharmProjects\agent-kit` and `D:\Marcin\PycharmProjects\rc-machines`.

Read `.scratch/agent-kit/design.md` (in rc-machines) sections 2, 4 and 8 first. Workflow changes are now made in the agent-kit repo, so that repo needs its own tracker, guardrails and agent instructions. It gets them the same way any project does: `agent-kit init`. The open workflow issue moves there.

1. **Init the kit repo.** In `D:\Marcin\PycharmProjects\agent-kit`:
   ```
   $env:PYTHONPATH = "D:\Marcin\PycharmProjects\agent-kit\src"
   python -m agent_kit init
   ```
   Expected: no conflicts; `AGENTS.md`, `GLOSSARY.md`, `docs/agents/project.md` created (the repo has none yet; if it has, stop and ask). Do not use `--force`.
2. **Project rules for the kit repo.** Fill `docs/agents/project.md`:
   - `## Tests`: `python -m unittest discover -s tests -t . -v` from the repo root; set `SKIP_PACKAGING_TEST=1` to skip the wheel build.
   - `## Do not edit`: `.agents/kit/` and `.agents/skills/` are this repo's **installed copy** of the kit. The source is `src/agent_kit/payload/`. Change the payload, then run `python -m agent_kit update` (with `PYTHONPATH=src`) to refresh the installed copy, and commit both.
   - `## Release`: the version lives in `src/agent_kit/__init__.py` and `pyproject.toml`; bump both together; the user tags `vX.Y.Z` on `dev`. Skills are refreshed with `python tools/refresh_skills.py <sha>`, never edited by hand.
   - `## Other rules`: Python 3.14 compatibility and stdlib only (design §2); the design of the kit is recorded in `README.md`.
3. **AGENTS.md.** Replace the `## Project` placeholder (outside the markers) with: "agent-kit: the project-agnostic agent setup (workflow docs, guardrails, skill library) and the `agent-kit` tool that installs it into projects. Project rules: `docs/agents/project.md`."
4. **GLOSSARY.md.** Add the terms that are specific to maintaining the kit: **Payload** (`src/agent_kit/payload/`, the files the tool installs, the source of truth), **Installed copy** (`.agents/kit/` and `.agents/skills/` in this repo, produced from the payload by `agent-kit update`, never edited by hand), **Skills snapshot** (the vendored copy of Matt Pocock's skills at a pinned commit, recorded in `UPSTREAM`).
5. **Move the open workflow issue.** Copy rc-machines `.scratch/review-workflow/issues/01-review-bookkeeping-friction.md` to the agent-kit repo at the same path. In the copy:
   - `scripts/check_tracker.py` → `.agents/kit/check_tracker.py`; `docs/adr/0004-workflow-state-machine.md` → `.agents/kit/adr/0004-workflow-state-machine.md`; `docs/agents/domain.md` → `.agents/kit/domain.md`. The ADR and the doc are payload files, so name their payload paths too: `src/agent_kit/payload/kit/…`.
   - The reference to `.scratch/front-loader/retro-2026-10-15-issue-001-session.md` becomes "the front-loader retro of 2026-10-15 in the rc-machines repo (`.scratch/front-loader/retro-2026-10-15-issue-001-session.md`)".
   - Keep `Labels: needs-triage` and `Status: draft` unchanged.
   Then in rc-machines, `git rm` the original, and remove the now-empty `.scratch/review-workflow/` folder if `issues/closed/` is the only thing left there. **Keep** `.scratch/review-workflow/issues/closed/02-pickup-tie-break.md` in rc-machines (closed issues stay where they closed).
6. **Commit** in each repo on `agent/agent-kit`. The kit repo's commit now runs its own installed hook; it must pass without `--no-verify`.

## Blocked by

- `agent-kit/09-rc-machines-adopts-the-kit` — both edit rc-machines on the same branch; 09 must be done first.

## Acceptance criteria

- [x] The agent-kit repo has `.agents/kit/`, `.agents/skills/`, `.agents/kit.lock`, `AGENTS.md` with the kit block, `GLOSSARY.md`, `docs/agents/project.md`, `docs/adr/.gitkeep`, `.scratch/.gitkeep`, and `core.hooksPath` = `.agents/kit/hooks`.
- [x] `python -m agent_kit update` (with `PYTHONPATH=src`) right after init reports no local changes and exits 0.
- [x] The installed copy matches the payload: for every file under `src/agent_kit/payload/kit/` and `payload/skills/`, the installed file is byte-identical.
- [x] `review-workflow/01` exists in agent-kit with its paths rewritten, and is gone from rc-machines' `issues/`; rc-machines' closed `02-pickup-tie-break.md` is untouched.
- [x] The test suites of both repos pass.

## Out of scope

- Working `review-workflow/01` itself.
- A check that the installed copy is in sync with the payload on every commit (possible follow-up; record it in the review summary if you think it is needed).

## Review

Implementation complete, submitted for review.

### Summary of changes

agent-kit, two commits on `agent/agent-kit`:

- `704e5cb` — `chore: adopt the agent kit`. `agent-kit init` (with `PYTHONPATH=src`) installed `.agents/kit/`, `.agents/skills/`, `.agents/kit.lock`, `AGENTS.md` from the template, `GLOSSARY.md`, `docs/agents/project.md`, `docs/adr/.gitkeep` and `.scratch/.gitkeep`; it appended `.agents/kit/hooks/* text eol=lf` to `.gitattributes` and set `core.hooksPath` to `.agents/kit/hooks`. The project-owned files were then filled in:
  - `docs/agents/project.md`: tests (`py -3.14 -m unittest discover -s tests -t . -v`; `SKIP_PACKAGING_TEST=1` skips the wheel build), do-not-edit (`.agents/kit/` and `.agents/skills/` are the installed copy, the source is `src/agent_kit/payload/`, refresh with `agent-kit update` and commit both), release (version in `src/agent_kit/__init__.py` and `pyproject.toml`, the user tags `vX.Y.Z` on `dev`, skills via `tools/refresh_skills.py`), and other rules (Python 3.14, stdlib only, the design in `README.md`). The generated `## ADR numbering` section is kept.
  - `AGENTS.md`: the `## Project` placeholder replaced with the ticket's sentence. The kit block was not edited.
  - `GLOSSARY.md`: **Payload**, **Installed copy** and **Skills snapshot** added.
- `bc7c783` — `docs: move review-workflow/01 to the kit repo`. The issue moved to `.scratch/review-workflow/issues/01-review-bookkeeping-friction.md`; `check_tracker.py`, the 0004 ADR and `domain.md` name their installed and payload paths, and the retro reference is explicit. `Labels: needs-triage` and `Status: draft` are unchanged. `.scratch/.gitkeep` is in this commit too.

rc-machines, one work commit on `agent/agent-kit` (the submission commit carries this ticket update):

- `37abd31` — `chore: move review-workflow/01 to the agent-kit repo`. `git rm` of the original; the closed `02-pickup-tie-break.md` is untouched. The `.scratch/review-workflow/` folder stays because it still holds `issues/closed/`.

### Verification

| Check | Result |
| --- | --- |
| `init` output | no conflicts; `AGENTS.md`, `GLOSSARY.md` and `docs/agents/project.md` created; exit 0 |
| `py -3.14 -m agent_kit update` (with `PYTHONPATH=src`) right after init | "Updated agent-kit from 0.1.0 to 0.1.0"; no local changes; exit 0 |
| Payload vs installed copy, every file under `payload/kit/` and `payload/skills/` | byte-identical (`sha256`); `.agents/kit/harness.sh` is the only generated extra |
| `git config core.hooksPath` in agent-kit | `.agents/kit/hooks` |
| `.agents/kit/check_tracker.py` in agent-kit | exit 0 |
| Kit hook runs on commit | probe: a staged ticket with `Status: nope` was refused by the repo's own hook (`unknown status 'nope'`), then removed |
| agent-kit suite | 106 tests, OK, exit 0 (1 skipped: POSIX mode bits on Windows) |
| rc-machines suite (`python -m unittest discover -s testing -t . -v`) | 79 tests, OK, exit 0 |
| Commits | both agent-kit commits and the rc-machines commit passed the hook without `--no-verify` |

### Notes for the reviewer

1. **Interpreter.** The ticket writes `python` for `init` and `update`, but on this machine `python` is 3.8.1 and cannot import `agent_kit`; design §2 and the README use `py -3.14`. I ran both with `py -3.14` and recorded that in `docs/agents/project.md`. `python -m agent_kit update` as written would fail here for the same reason.
2. **The folder to remove.** Step 5 says to remove `.scratch/review-workflow/` if `issues/closed/` is the only thing left, and also to keep `02-pickup-tie-break.md`. The two conflict, so I kept the folder. Git tracks only the file, so the empty `issues/` directory does not affect the commit.
3. **Follow-up: an installed-copy sync check.** I think it is worth having. Editing `src/agent_kit/payload/` and forgetting `agent-kit update` leaves this repo's installed copy stale, and only the acceptance check above would catch it. A `tests/` case comparing the two trees (normalising CRLF to LF) would turn that into a red test instead of a review finding. Cut as `agent-kit/12-installed-copy-sync` in the agent-kit repo (`.scratch/agent-kit/issues/12-installed-copy-sync.md`), `Status: awaiting-agent`.
