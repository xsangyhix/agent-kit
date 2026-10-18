Status: done

## Description

**Where to work:** `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`. Ticket status changes go in rc-machines (`D:\Marcin\PycharmProjects\rc-machines`) on `agent/agent-kit`.

Read `.scratch/agent-kit/design.md` (in rc-machines) sections 4–9 first. **Design §9 is the specification for this ticket.** Work test-first. Reuse what ticket 06 built (`lock.py`, `confirm_deletion`, the kit block functions, the copy steps); if init's steps are not callable on their own, extract them into functions shared by `init` and `update` rather than copying code.

Implement `installer.update(root, force, stdin, stdout) -> int` and wire the `update` subcommand in `cli.py`.

Tests in `tests/test_update.py`. Set up each case by running `installer.init` into a throwaway git repo, then change things. To simulate a newer kit, make the payload root a parameter (for example an optional `payload` argument to `init`/`update`, defaulting to `payload_root()`) and point it at a modified copy of the payload in a temp folder: change one file, add one, remove one, and bump the version passed in. Cover at least:

- no local changes, new payload: changed file updated, added file present, removed file gone, lock rewritten with the new hashes and version, exit 0, message "Updated agent-kit from X to Y.";
- no lock: exit 2 with the message from design §9;
- unknown harness in the lock: exit 2;
- a kit file edited locally (one character): exit 1, the path listed as modified, nothing changed;
- a kit file deleted locally: exit 1, listed as missing;
- an extra file added under `.agents/skills/`: exit 1, listed as not installed by agent-kit;
- the kit block edited inside the markers: exit 1, listed;
- a line ending change only (rewrite a kit file with `\r\n`): **not** a local change, exit 0;
- `--force` with `isatty()` false: exit 1, nothing changed;
- `--force`, `isatty()` true, `yes`: local edits discarded, kit updated, exit 0;
- project-owned files (`GLOSSARY.md`, `docs/agents/project.md`, text outside the markers in `AGENTS.md`, `.agents/hooks.local/pre-commit`) are byte-identical after every update;
- `core.hooksPath` is reset to `.agents/kit/hooks` if it was changed.

## Blocked by

- `agent-kit/06-init-command`

## Acceptance criteria

- [x] Every behaviour in design §9 has a test, and the whole suite passes.
- [x] Nothing is written when any check fails.
- [x] No project-owned file changes on update (asserted byte for byte).
- [x] The code targets Python 3.14, as design §2 and `pyproject.toml` require (Q1).

## Out of scope

- Downgrading checks, or migrations between lock formats (there is only one format).
- Re-creating missing templates on update.

## Questions

**Q1 - Python floor: 3.8 or 3.14?** The acceptance criteria said "No code uses a feature newer than Python 3.8", but design §2 says every file targets **Python 3.14** (decided 2026-10-18), matching the answer to ticket 06 Q1. **Recommended:** follow the design and rewrite the stale acceptance criterion. **Answer:** accepted, 2026-10-18: target Python 3.14; the 3.8 acceptance criterion is rewritten above.

## Review

Implementation complete, submitted for review.

### Summary of changes

- `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`: one commit, `09467e4` — `feat: add the update command`.
  - `src/agent_kit/installer.py` — `update(root, force, stdin, stdout, payload=None)` implementing design §9 in order: git root, lock, harness, local changes (files, extras, block), force confirmation, bad markers, then replace the two kit folders and run init steps 1, 2, 4, 6, 7 and 8. Init's copy, harness, block and hooks-path steps are extracted into `_copy_payload()`, `_write_kit_block()`, `_set_hooks_path()` and `_kit_owned_hashes()`, shared by both commands. `init()` gained the same optional `payload` argument.
  - `src/agent_kit/cli.py` — `update` wired to `installer.update`.
  - `tests/test_update.py` — 19 tests: the happy path, reporting, project-owned files, missing/invalid lock, unknown harness, every local-change kind, line endings, `--force` (non-tty, `no`, `yes`), templates, and `core.hooksPath`.
  - `tests/test_cli.py` — the "update is not implemented" test is replaced by one that checks the wiring.
- This ticket — Q1 answered, criteria ticked, status and label moved for review.

### Verification

| Check | Result |
| --- | --- |
| `py -3.14 -m unittest tests.test_update -v` (red before the implementation, green after) | 19 tests, OK |
| `py -3.14 -m unittest discover -s tests -t . -v` | 104 tests, OK, exit 0 (1 skipped: POSIX mode bits on Windows) |
| Manual check — new empty repo, `PYTHONPATH=src py -3.14 -m agent_kit init <path>` | exit 0; then `update <path>` printed "Updated agent-kit from 0.1.0 to 0.1.0." and exit 0 |
| Manual check — `git config core.hooksPath` after update | `.agents/kit/hooks` |
| Manual check — append one line to `.agents/kit/workflow.md`, then `update` | exit 1; path listed as `(modified)`; nothing changed |
| Manual check — same edit, then `update --force` without typing an answer | prompt shown, stdin at EOF, "Aborted. Nothing was changed.", exit 1 |
| Refusal tests | each snapshots the whole tree (excluding `.git`) and asserts it is byte-identical after the refusal |

### Notes for the reviewer

1. **`payload` is an optional argument on both commands**, defaulting to `payload_root()`. Tests point it at a copied payload with one file changed, one added, one removed and a bumped version (via `mock.patch.object(installer, "__version__", ...)`).
2. **The block hash matches init's.** `_block_text()` takes the text between the marker lines and drops the newline that ends the begin-marker line, so the hashed text is the block content plus its trailing newline — exactly what init stores.
3. **Missing markers are a local change** ("kit block missing markers"). A malformed marker state is not listed as a local change but refused by design §9 step 5. That refusal comes after the `--force` confirmation and before anything is deleted, so "nothing is written when any check fails" still holds.
4. **`--force` confirms the changed paths**, not the two folders: those are the files whose local content is discarded. The two folders are then replaced wholesale, as §9 says.
5. **The summary's file lists compare the old lock with the new files.** A locally edited file that the new kit version does not change is restored but does not appear under `Updated:`.
6. **Templates are never written by update**, including when a project deleted one; a test pins that.
7. **`core.hooksPath` is set after the copy**, so a failed `git config` leaves the same partial state init already allows. It is the only step that can fail after writing starts.
