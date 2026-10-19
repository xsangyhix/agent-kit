Status: done

## Description

Two small changes to the kit's pre-commit hook, `src/agent_kit/payload/kit/hooks/pre-commit`, both from the 2026-10-18 code review of the agent-kit effort.

### 1. Explain the interpreter probe

Design §11 step 5 says "then `python3` on PATH". The hook instead runs `python3 --version` and uses `python3` only if that succeeds. This skips the Microsoft Store `python3` alias on Windows, which exists on PATH but fails when run. The reason is sound, but it is written down only in ticket 03's notes, so the deviation looks accidental. The user accepted it on 2026-10-18 during the review:

- Add a short comment above the probe saying why it runs `--version` rather than checking that the command exists.
- Note in `README.md`'s hook description that `python3` is used only when it actually runs.

Do not edit the rc-machines design file.

### 2. Share the protected branch with the local hook

The hook keeps `PROTECTED_BRANCH=dev` local and exports only `PYTHON` and `branch` to `.agents/hooks.local/pre-commit`. A project's local hook that needs the protected branch must therefore hard-code `dev`, as rc-machines does today, and the two copies can drift apart. Export `PROTECTED_BRANCH` alongside `PYTHON` and `branch`, and document it:

- in the hook's step-4 comment;
- in `README.md`'s "Project-specific steps" section.

This amends design §11 step 7 (`export PYTHON branch`). The user approved it on 2026-10-18.

Backwards compatibility: purely additive. Existing local hooks ignore the new variable.

The hook is payload, so refresh this repo's installed copy with `PYTHONPATH=src py -3.14 -m agent_kit update` and commit both (`docs/agents/project.md`). The hook must stay POSIX `sh` with LF line endings.

Test-Driven Development: add a test in `tests/guardrail/test_pre_commit_hook.py` showing that a local hook sees `PROTECTED_BRANCH=dev`.

## Blocked by

None.

## Acceptance criteria

- [x] A local hook that prints `$PROTECTED_BRANCH` prints `dev`. A test covers it.
- [x] The probe comment exists, and the hook's behaviour is otherwise unchanged (existing hook tests pass).
- [x] `README.md` documents the probe and the exported `PROTECTED_BRANCH`.
- [x] The hook is LF only, and `.agents/kit/hooks/pre-commit` is identical to the payload, with `.agents/kit.lock` matching.
- [x] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Making the protected branch configurable (design §13).
- The executable bit of the installed hook (agent-kit/11-kit-hook-executable-bit).
- Changing rc-machines' local hook (agent-kit/22-rc-machines-takes-the-kit-fixes).

## Review

Implementation complete, submitted for review.

### Summary of changes

`src/agent_kit/payload/kit/hooks/pre-commit`:

- **The interpreter probe is explained.** The comment above step 3 now says why it runs `python3 --version` rather than checking that the command exists: on Windows the Microsoft Store alias sits on PATH but fails when run, so it would win.
- **The protected branch is exported.** Step 4 now exports `PYTHON branch PROTECTED_BRANCH`, and its comment says local hooks see all three.

`README.md`:

- The hook description says the checks use the project's `.venv` interpreter when there is one, otherwise `python3` only when that command actually runs, then `python`.
- "Project-specific steps" now lists `PROTECTED_BRANCH` alongside `PYTHON` and `branch`.

`tests/guardrail/test_pre_commit_hook.py`:

- `LocalHookTests.test_local_hook_sees_the_protected_branch` writes a local hook that prints `$PROTECTED_BRANCH` and asserts it prints `dev`.

`.agents/kit/hooks/pre-commit` and `.agents/kit.lock` were refreshed with `PYTHONPATH=src py -3.14 -m agent_kit update`. The change is purely additive; existing local hooks ignore the new variable.

### Verification

TDD: the new test failed first (`'' != 'dev'`), then passed once `PROTECTED_BRANCH` was exported.

- `py -3.14 -m unittest tests.guardrail.test_pre_commit_hook -v`: 19 tests, OK.
- `py -3.14 -m unittest discover -s tests -t . -v`: 166 tests, OK (skipped=1). The skip is the pre-existing Windows-only on-disk mode test.
- `PYTHONPATH=src py -3.14 -m agent_kit update` exits 0, and `.agents/kit/hooks/pre-commit` is identical to the payload.
- `py -3.14 tools/check_payload_sync.py` exits 0.
- The payload hook has no CR bytes: 0 CRLF pairs, 0 CR bytes.
