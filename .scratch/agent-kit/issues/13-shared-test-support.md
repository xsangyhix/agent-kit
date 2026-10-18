Labels: ready-for-agent
Status: awaiting-agent

## Description

Prefactor before tickets 14–17, which all add installer tests. Found in the 2026-10-18 code review of the agent-kit effort (Standards axis, Duplicated Code).

`tests/test_init.py` and `tests/test_update.py` each define their own copy of the same helpers: `sha256_text`, `sha256_file`, `read_text`, `block_content`, a `FakeStdin` whose `isatty` is controllable, the lock-data helper and the payload-copy helper. `tests/guardrail/test_pre_commit_hook.py` defines `make_repo` three times, once per test class.

Move the shared helpers into one support module for the installer tests (beside or inside `tests/guardrail/support.py`, which already holds `GitRepo`; choose by what reads best and say why in the review). Where two copies differ (for example `block_content` takes a `payload` argument in `test_update.py` only), keep the more general form. Collapse the three hook-test `make_repo` methods into one helper; if their bodies differ, parametrise the difference rather than keeping three copies.

This is a test-only refactor: no file under `src/`, `tools/` or `.agents/` changes.

## Blocked by

None.

## Acceptance criteria

- [ ] Each helper listed above exists once under `tests/`, and `test_init.py` and `test_update.py` import it.
- [ ] `test_pre_commit_hook.py` has one repo-building helper instead of three `make_repo` methods.
- [ ] The test count is unchanged and every test that passed before still passes: `py -3.14 -m unittest discover -s tests -t . -v` (record the before and after counts in the review).
- [ ] No file outside `tests/` changes.

## Out of scope

- Changing what any test asserts, or adding tests.
- Refactoring `tests/test_packaging.py`, `tests/test_templates.py` or `tests/test_refresh_skills.py` beyond switching to a shared helper they already duplicate.
