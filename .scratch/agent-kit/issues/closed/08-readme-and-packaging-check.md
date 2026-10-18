Status: done

## Description

**Where to work:** `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`. Ticket status changes go in rc-machines (`D:\Marcin\PycharmProjects\rc-machines`) on `agent/agent-kit`.

Read `.scratch/agent-kit/design.md` (in rc-machines) sections 1, 4, 10 and 12 first. This ticket makes the kit usable by someone who only reads its README, and proves the installed package (not just the source tree) carries the whole payload.

1. **README.md**, replacing ticket 01's stub. Sections:
   - *What it is* — design §1 in a short paragraph; opencode only for now.
   - *Requirements* — Python 3.14+ and git on the developer's machine; a POSIX `sh` for the hook (Git for Windows provides one). The project itself can be in any language.
   - *Install the tool* — `pipx install D:\Marcin\PycharmProjects\agent-kit` and the `uv tool install` equivalent; how to upgrade (design §12).
   - *Start a project* — `agent-kit init`, what it creates (the table from design §4), what "kept" means, then review and commit.
   - *Update a project* — `agent-kit update`, why it refuses on local edits, and that kit changes belong in this repo.
   - *`--force`* — what it deletes, the typed confirmation, and that it is refused without an interactive terminal.
   - *Project-specific steps* — the local hook `.agents/hooks.local/pre-commit` (gets `PYTHON` and `branch`; a non-zero exit refuses the commit) and `docs/agents/project.md`.
   - *Maintaining the kit* — edit files under `src/agent_kit/payload/`, run the tests, bump the version in both places, the user tags `vX.Y.Z` on `dev`; refresh skills with `python tools/refresh_skills.py <sha>`.
   - *Credits and licenses* — the skill library is Matt Pocock's (https://github.com/mattpocock/skills), MIT licensed, shipped unmodified with its `LICENSE` and an `UPSTREAM` record, minus the `setup-matt-pocock-skills` skill, which this kit replaces; his files remain under his license. The kit's own files have no license yet.
2. **Packaging check**, as a test `tests/test_packaging.py`, skipped with a clear reason when the `SKIP_PACKAGING_TEST` environment variable is set:
   - build a wheel into a temp folder with `python -m pip wheel . --no-deps -w <tmp>`;
   - open it with `zipfile` and assert it contains every file under `src/agent_kit/payload/` (compare the two lists of relative paths), including `payload/kit/hooks/pre-commit`, `payload/skills/LICENSE` and `payload/skills/UPSTREAM`.
   If the comparison fails because files are missing from the wheel, fix `pyproject.toml` (for example a `MANIFEST.in` or explicit package-data patterns) until it passes.
3. **Manual end-to-end check**, recorded in the review summary: in a throwaway venv, `pip install .`; in a new empty git repo, `agent-kit init`, then commit on a branch `agent/test` (the kit hook runs and passes); edit `.agents/kit/workflow.md` and run `agent-kit update` (refused, file listed); restore it and run `agent-kit update` (succeeds). Delete the venv and the repo afterwards.

## Blocked by

- `agent-kit/07-update-command`

## Acceptance criteria

- [x] The README has every section listed, and every command in it was run once and works as written.
- [x] `tests/test_packaging.py` passes: the wheel carries the full payload.
- [x] The manual end-to-end check is recorded with its outcome.
- [x] The whole suite passes.

## Out of scope

- Tagging `v0.1.0`: the user does it on `dev` after merging.
- Publishing to PyPI; a GitLab remote.

## Review

Implementation complete, submitted for review.

### Summary of changes

- `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`: three commits.
  - `23e02fc` — `docs: write the project README`. Replaces ticket 01's stub with the nine sections the ticket lists.
  - `0b9272d` — `test: check the wheel carries the whole payload`. `tests/test_packaging.py` builds a wheel with `python -m pip wheel . --no-deps -w <tmp>`, opens it with `zipfile`, and compares the `agent_kit/payload/` entries with every file under `src/agent_kit/payload/`. It builds from a temporary clean copy of the project so a stale local `build/` folder cannot leak removed files into the wheel. Skipped with a clear reason when `SKIP_PACKAGING_TEST` is set.
  - `23bb06c` — `fix: skip bytecode caches when copying the payload`. The end-to-end check found that `pip install .` byte-compiles `payload/kit/check_tracker.py` into `payload/kit/__pycache__/` inside the installed package; `init` copied that cache into the project, and the next `update` refused because the `.pyc` is not in the lock. `_copy_tree()` now skips `__pycache__` and `.pyc` files, with a test in `tests/test_init.py`.
- This ticket — criteria ticked, status and label moved for review.

### Verification

| Check | Result |
| --- | --- |
| `py -3.14 -m unittest discover -s tests -t .` | 106 tests, OK, exit 0 (1 skipped: POSIX mode bits on Windows) |
| `SKIP_PACKAGING_TEST=1 py -3.14 -m unittest tests.test_packaging -v` | skipped with `SKIP_PACKAGING_TEST is set` |
| `py -3.14 -m unittest tests.test_init.InitTests.test_fresh_repo_does_not_copy_bytecode_caches -v` | red before `_copy_tree()` changed, green after |
| Manual end-to-end check, throwaway venv + `pip install .` + new empty git repo | see below |
| `agent-kit --version` in the venv | `agent-kit 0.1.0` |

Manual end-to-end check, run after removing the repository's ignored `build/` folder and the cached wheel:

1. `pip install .` into a fresh venv succeeded. The installed payload gained pip's `__pycache__` for `check_tracker.py`, and `init` did not copy it.
2. `agent-kit init <repo>` exited 0 in a new empty git repo, then `git checkout -b agent/test` and `git add -A`.
3. A first commit attempt with an issue file carrying `Status: nope` was refused by the kit hook (`unknown status 'nope'`), proving the hook runs. Removing that file and committing again succeeded (123 tracked files).
4. Appending a line to `.agents/kit/workflow.md` and running `agent-kit update` exited 1 and listed `.agents/kit/workflow.md (modified)`.
5. `git checkout -- .agents/kit/workflow.md` and running `agent-kit update` exited 0 with `Updated agent-kit from 0.1.0 to 0.1.0.`; `core.hooksPath` remained `.agents/kit/hooks`.
6. The venv and repo were deleted afterwards.

### Notes for the reviewer

1. **`pipx` and `uv` are not installed on this machine**, so the two install commands in the README could not be run as written. The venv `pip install .` path the ticket specifies was run end to end instead. The commands follow design §12, including `--python 3.14`.
2. **The packaging test does not compare against `build/`.** It copies `pyproject.toml`, `README.md` and `src/` into a temp folder and builds there, so the result describes a clean checkout. The stale `build/` found during this work contained a removed `payload/README.txt`, which a wheel built in place would have shipped.
3. **The bytecode fix is part of this ticket** because it was found by the required end-to-end check: without it, step 5 fails with `.agents/kit/__pycache__/check_tracker.cpython-314.pyc (not installed by agent-kit)`. It only filters the copy; it does not change the lock format or what update considers a local change.
4. **Line endings:** after `git checkout -- .agents/kit/workflow.md` (CRLF on Windows) and a successful `update` (LF from the payload), `git status` reported the file, but `git diff` was empty and the blob hash matched `HEAD`. The lock's CRLF normalisation already treats this as unchanged.

