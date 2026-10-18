Status: done

## Description

**Where to work:** `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`. Ticket status changes go in rc-machines (`D:\Marcin\PycharmProjects\rc-machines`) on `agent/agent-kit`.

Read `.scratch/agent-kit/design.md` (in rc-machines) section 10 and `.scratch/agent-kit/research-2026-10-18-upstream-and-opencode.md` first. This ticket adds Matt Pocock's skill library to the kit, **verbatim and with its MIT license**, through a maintainer tool so later refreshes are one command.

1. Write `tools/refresh_skills.py` (stdlib only, Python 3.14 per design §2; the 3.8 floor was replaced on 2026-10-18):
   - Usage: `python tools/refresh_skills.py <commit-sha> [--archive PATH]`. The SHA must be 40 hex characters, otherwise exit 2.
   - Without `--archive`, download `https://codeload.github.com/mattpocock/skills/tar.gz/<sha>` with `urllib.request` into a temp file. With `--archive`, read that local `.tar.gz` instead (this is how tests run offline).
   - The archive's single top folder is `skills-<sha>/` (do not hard-code the name: take the first path component and require every member to share it).
   - Build the new snapshot in a temporary folder: copy `skills/engineering/`, `skills/productivity/`, `skills/misc/`, `skills/in-progress/` with all contents, except the folder `skills/engineering/setup-matt-pocock-skills/`; copy top-level `LICENSE` to `LICENSE`; write `UPSTREAM` exactly as in design §10, with today's date. Copy file bytes unchanged.
   - Refuse (exit 1, nothing changed) if: `LICENSE` is missing from the archive; any of the four category folders is missing; any member path is absolute or contains `..`; or the result has a file directly under its root ending in `.md`.
   - Only after all checks pass, replace `src/agent_kit/payload/skills/` with the temporary folder.
   - Print the number of skills copied (folders containing `SKILL.md`).
2. Tests in `tests/test_refresh_skills.py`, using small `.tar.gz` fixtures built in the test with `tarfile` (no network): the happy path (categories copied, `deprecated/` and `setup-matt-pocock-skills/` absent, `LICENSE` byte-identical, `UPSTREAM` content); a missing `LICENSE` refused with the payload unchanged; a `..` member refused; a bad SHA → exit 2. Make the tool's target folder a parameter of its main function, so tests write into a temp folder and never touch the real payload.
3. Run it for real: `python tools/refresh_skills.py 49dd158d1076134a641b33efb035946536778336`. Commit the resulting `src/agent_kit/payload/skills/` in its own commit, message `chore: vendor mattpocock/skills at 49dd158`.

## Blocked by

- `agent-kit/01-kit-repo-skeleton`

## Acceptance criteria

- [x] `src/agent_kit/payload/skills/LICENSE` is byte-identical to `https://raw.githubusercontent.com/mattpocock/skills/49dd158d1076134a641b33efb035946536778336/LICENSE`.
- [x] `src/agent_kit/payload/skills/UPSTREAM` matches design §10 and names the full SHA.
- [x] The snapshot has `engineering/`, `productivity/`, `misc/`, `in-progress/`; no `deprecated/`; no `setup-matt-pocock-skills/`; no `*.md` directly under `payload/skills/`.
- [x] Spot-check: `engineering/tdd/SKILL.md` is byte-identical to upstream's `skills/engineering/tdd/SKILL.md` at that commit.
- [x] The test suite passes offline.

## Out of scope

- Editing any skill file (verbatim is the point).
- Installing the snapshot into a project (ticket 06).

## Review

Implementation complete, submitted for review.

### Summary of changes

- `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`:
  - `e8fab5f` — `tools/refresh_skills.py` and `tests/test_refresh_skills.py`. The tool downloads or reads an archive, validates it, builds the snapshot in a staging folder, and only then swaps it in. `main(argv, *, target=...)` makes the destination an argument so tests never touch the real payload.
  - `0d08a4a` — `src/agent_kit/payload/skills/`, 102 files (LICENSE, UPSTREAM, four categories, 37 skills), vendored verbatim at `49dd158`.
  - `3f526b1` — review fixes: dropped an unused parameter, restore the previous snapshot if the swap fails, count skill folders rather than `SKILL.md` files.
- This ticket — 3.8 replaced with 3.14 in the tool bullet (design §2), status and label moved for review.

### Verification

| Check | Result |
| --- | --- |
| `py -3.14 -m unittest discover -s tests -t . -v` from agent-kit | 37 tests, OK, exit 0 |
| `py -3.14 tools/refresh_skills.py 49dd158d1076134a641b33efb035946536778336` | `Copied 37 skills`, exit 0 |
| Snapshot file count | 102 files: LICENSE, UPSTREAM, 4 category folders |
| `LICENSE` SHA-256 vs upstream raw URL | `0e7ac423…dbbb5`, identical |
| `engineering/tdd/SKILL.md` SHA-256 vs upstream raw URL | `5505d25b…922e0`, identical |
| Second real run after the review fixes | `git status` showed no payload change, so the snapshot is reproducible |
| Root of `payload/skills/` | only LICENSE and UPSTREAM files; no `*.md` |
| `deprecated/`, `engineering/setup-matt-pocock-skills/` | absent |
| Refusal tests | missing LICENSE, missing category, `..` member, absolute member, two top folders, bad SHA (2) — all pass |

### Notes for the reviewer

1. **Python floor.** The ticket still named 3.8, but design §2 was changed to 3.14 for every file on 2026-10-18 (ticket 01, Q9). I updated the description to match, as ticket 03 did, rather than asking again.
2. **Extra tests.** Beyond the four the ticket lists, the suite locks the other refusals it specifies: missing category, absolute member, and two top folders. The happy-path test also proves a stale payload is replaced.
3. **Staging.** The snapshot is built in a temporary sibling folder under `payload/` so the final rename stays on one filesystem; the old snapshot is renamed aside first and restored if the swap fails. A hard kill could leave a dot-prefixed staging folder, which the next run does not clean up.
4. **UPSTREAM date.** `fetched: 2026-10-18` is today's date at refresh time; a later refresh rewrites it.

