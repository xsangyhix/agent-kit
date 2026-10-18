Status: done

## Description

Prefactor before tickets 14–17, which all add installer tests. Found in the 2026-10-18 code review of the agent-kit effort (Standards axis, Duplicated Code).

`tests/test_init.py` and `tests/test_update.py` each define their own copy of the same helpers: `sha256_text`, `sha256_file`, `read_text`, `block_content`, a `FakeStdin` whose `isatty` is controllable, the lock-data helper and the payload-copy helper. `tests/guardrail/test_pre_commit_hook.py` defines `make_repo` three times, once per test class.

Move the shared helpers into one support module for the installer tests (beside or inside `tests/guardrail/support.py`, which already holds `GitRepo`; choose by what reads best and say why in the review). Where two copies differ (for example `block_content` takes a `payload` argument in `test_update.py` only), keep the more general form. Collapse the three hook-test `make_repo` methods into one helper; if their bodies differ, parametrise the difference rather than keeping three copies.

This is a test-only refactor: no file under `src/`, `tools/` or `.agents/` changes.

## Blocked by

None.

## Acceptance criteria

- [x] Each helper listed above exists once under `tests/`, and `test_init.py` and `test_update.py` import it.
- [x] `test_pre_commit_hook.py` has one repo-building helper instead of three `make_repo` methods.
- [x] The test count is unchanged and every test that passed before still passes: `py -3.14 -m unittest discover -s tests -t . -v` (record the before and after counts in the review).
- [x] No file outside `tests/` changes.

## Out of scope

- Changing what any test asserts, or adding tests.
- Refactoring `tests/test_packaging.py`, `tests/test_templates.py` or `tests/test_refresh_skills.py` beyond switching to a shared helper they already duplicate.

## Review

Implementation complete, submitted for review.

### Summary of changes

One test-only commit. The shared helpers now live in `tests/guardrail/support.py`:

- `sha256_text`, `sha256_file`, `read_text`, `block_content`, `lock_data`, `copied_payload`, `FakeStdin` and `make_repo` each exist once, and `tests/test_init.py` and `tests/test_update.py` import them.
- `block_content` and `copied_payload` keep the more general form from `test_update.py`: both take an optional payload, defaulting to the repo payload.
- `copied_payload` and `make_repo` take the test case and register their cleanup through `addCleanup`, preserving the existing lifecycle.
- The three identical `make_repo` methods in `tests/guardrail/test_pre_commit_hook.py` are gone; every test calls `support.make_repo(self, <branch>)`.
- The now-unused `REPO_ROOT`/`PAYLOAD` constants in `test_update.py` and `AGENTS_BLOCK` in `test_init.py` were removed.

**Why `tests/guardrail/support.py` and not a new module beside it:** it already holds `GitRepo`, which both installer tests import, and `AI_MARKERS`/`find_shell`, which `test_init.py` imports. A second support module would split one dependency graph across two files for no gain; the module docstring now says it is suite-wide support.

### Verification

| Check | Before | After |
| --- | --- | --- |
| `py -3.14 -m unittest discover -s tests -t . -v` | 106 tests, 91 passed, 15 failed, 1 skipped | 106 tests, 91 passed, 15 failed, 1 skipped — same failure set |
| Same command with Git's `sh.exe` and Python 3.14 on `PATH` | not run | 106 tests, 104 passed, 1 failed, 1 skipped |

The 15 failures are pre-existing and environmental, not caused by this refactor:

- 14 are `find_shell()` finding the WSL `bash` stub (`Windows Subsystem for Linux has no installed distributions`) — `sh` is absent and `shutil.which("bash")` returns `C:\Windows\system32\bash.EXE`. With Git's `sh.exe` on `PATH` those tests pass, which is the second row above.
- `test_a_line_ending_change_only_is_not_a_local_change` fails because this clone has `core.autocrlf=true`, so the payload's `workflow.md` is CRLF on disk; the test's blind `replace(b"\n", b"\r\n")` turns CRLF into CRCRLF, which the lock normalisation then sees as modified. Both the unrefactored and refactored suites fail it identically.

`git status --short` shows only the four `tests/` files and this ticket file; nothing outside `tests/` changed.
