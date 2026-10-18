Labels: ready-for-human
Status: in-review

## Description

The suite fails 15 tests in the project's Windows development environment (PyCharm running `.venv\Scripts\python.exe`, Git's folders not on `PATH`). All three causes are in the test support, not in the kit: `agent-kit/13-shared-test-support`'s review recorded the first two as an accepted baseline and this ticket removes them.

1. **The WSL launcher answers to `bash`.** `tests/guardrail/support.py`'s `find_shell()` looks for `sh`, then `bash`, on `PATH`, and only falls back to Git's own `sh.exe` when neither is found. On Windows, `C:\Windows\System32\bash.exe` is the WSL launcher: it exits `1` with `Windows Subsystem for Linux has no installed distributions` and cannot run a Windows path. Every test that runs the hook then fails — 14 of the 15. On Windows, prefer Git's `sh.exe` before consulting `PATH`.

2. **The hook resolves the Windows Store Python alias.** The hook picks its interpreter from `.venv/Scripts/python.exe`, `.venv/bin/python`, `python3`, then `python`. The throwaway repositories the hook tests create have no `.venv`, and PyCharm does not put the selected interpreter's folder on `PATH`, so the hook reaches the `python` alias, which prints the Microsoft Store message and fails. The test harness should put the interpreter running the tests (`sys.executable`) on the hook's `PATH`. This affects `GitRepo.run_hook` and the env built inline by `tests/test_init.py::test_the_installed_hook_passes_on_the_freshly_initialised_repo`.

3. **The CRLF test assumes an LF working tree.** `tests/test_update.py::test_a_line_ending_change_only_is_not_a_local_change` rewrites the installed `workflow.md` with a blind `replace(b"\n", b"\r\n")`. In a clone with `core.autocrlf=true` the file is already CRLF, so the test writes CRCRLF and `update` correctly reports a modification. Normalise the endings to LF before converting.

## Blocked by

None.

## Acceptance criteria

- [x] On Windows, `find_shell()` returns Git's `sh.exe` even when the only `bash` on `PATH` is the WSL launcher; a unit test pins the choice.
- [x] The hook's test environment contains the running interpreter's folder on `PATH`, so the hook resolves a real Python when the tests run under `.venv`.
- [x] `test_a_line_ending_change_only_is_not_a_local_change` passes in a clone with `core.autocrlf=true`.
- [x] `py -3.14 -m unittest discover -s tests -t .` is green with the project's `.venv` interpreter and Git's folders absent from `PATH`; record the counts in the review.
- [x] The suite stays green with Git's `sh.exe` first on `PATH`; no regression.

## Out of scope

- Changing the installed hook's interpreter resolution in the payload; the test harness adapts to the hook, not the reverse.
- Removing the suite's dependency on a POSIX shell; the hook is a shell script.
- `tests/test_packaging.py`'s need for a wheel build and possible network access.

## Review

Implementation complete, submitted for review.

### Summary of changes

- `tests/guardrail/support.py`:
  - `find_shell()` now asks `_git_shell()` first on Windows, before consulting `PATH`. `_git_shell()` is the old Git-installation fallback, extracted unchanged so the unit test can pin it.
  - `hook_path(shell, current)` builds the PATH a hook run receives: the shell's folder, the running interpreter's folder (`sys.executable`), then the inherited PATH. `GitRepo.run_hook` uses it, which is what stops the hook reaching the Windows Store `python` alias under PyCharm.
- `tests/test_init.py` uses `hook_path` in the inline environment for `test_the_installed_hook_passes_on_the_freshly_initialised_repo`.
- `tests/test_update.py::test_a_line_ending_change_only_is_not_a_local_change` normalises the installed file to LF before converting to CRLF, so it behaves the same in a clone with `core.autocrlf=true` or `false`.
- `tests/guardrail/test_pre_commit_hook.py::FindShellTests` pins both branches: on Windows Git's `sh.exe` wins over a `bash` on `PATH`; on a POSIX platform the PATH shell still wins.

### Verification

| Check | Before | After |
| --- | --- | --- |
| `.venv\Scripts\python.exe -m unittest discover -s tests -t .` with Git's folders absent from `PATH` (the PyCharm setup) | 110 tests, 15 failed, 1 skipped | 112 tests, 0 failed, 1 skipped |
| With Git's `usr\bin` first on `PATH` (`test_pre_commit_hook` + `test_update`) | — | 39 tests, 0 failed |

The one skip is the POSIX-only on-disk mode test on Windows (`test_the_installed_hook_keeps_its_mode_on_disk`). The two added tests are `FindShellTests`.

