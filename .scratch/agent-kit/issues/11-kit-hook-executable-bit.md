Labels: ready-for-human
Status: in-review

## Description

**Where to work:** this repository, branch `agent/agent-kit`.

`agent-kit init` and `update` write `.agents/kit/hooks/pre-commit` with the right bytes and set mode `0o755` on disk (`installer._copy_payload`), but they never record that mode in the git index. On Windows (`core.filemode=false`) git records a newly added hook as `100644`, so a POSIX clone checks out a non-executable hook and git silently skips it: the agent-session `dev` gate, the `.scratch` gitignore check, the tracker check and the project's local hook all stop running with no warning.

Found 2026-10-18 (ticket 09 review, note 2). Ticket 09 worked around it only for its own project-owned hook, by hand.

Decided 2026-10-18 during the review: **the tool records the mode itself.** After `_copy_payload` chmods the hook, run `git -C <root> update-index --add --chmod=+x .agents/kit/hooks/pre-commit` in both `init` and `update` (`--add` covers a fresh install where the file is not yet indexed; on `update` it flips the bit on the already-tracked file). This amends design §8's "the tool never stages or commits" by the narrowest amount: it touches only the mode of the one hook file it just wrote, and never stages or commits anything else. Record the amendment in `README.md` (the kit's design record per `docs/agents/project.md`); do not edit the rc-machines `design.md`.

Test-Driven Development.

## Blocked by

- agent-kit/13-shared-test-support

## Acceptance criteria

- [x] After `init` in a fresh repo, `git ls-files -s .agents/kit/hooks/pre-commit` reports mode `100755`; a test asserts it by reading the index, not the filesystem bit.
- [x] After `update` over an existing install, the same check reports `100755`.
- [x] The on-disk mode stays `0o755` (the existing assertion holds).
- [x] `init` and `update` touch the index only for the hook path: `git status` shows no other file staged by the tool, and no commit is made.
- [x] `test_the_installed_hook_is_executable` no longer skips on Windows, and it inspects the index.
- [x] `README.md` records the index-mode step and the narrow exception to "never stages or commits", and gives the manual `git add --chmod=+x` step for a project-owned `.agents/hooks.local/pre-commit`.
- [x] After the fix, `PYTHONPATH=src py -3.14 -m agent_kit update` in the agent-kit repo re-records its own `.agents/kit/hooks/pre-commit` as `100755`; the repo's `git ls-files -s` shows `100755` for that path after committing.
- [x] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Fixing the mode of project-owned `.agents/hooks.local/pre-commit` automatically: the tool never writes that file, so it is documented, not fixed.
- Making the protected branch configurable (design §13).
- A POSIX CI job that checks out the committed tree and proves the hook runs (no POSIX runner exists here); the index-mode test is the proxy.
- Taking the fix into rc-machines' installed copy; that is agent-kit/22-rc-machines-takes-the-kit-fixes.

## Review

Implementation complete, submitted for review.

### Summary of changes

- `installer.HOOK` names the hook path once; `_copy_payload` still chmods it to `0o755`.
- `installer._record_hook_mode` runs `git -C <root> update-index --add --chmod=+x .agents/kit/hooks/pre-commit`. Both `init` and `update` call it right after `_copy_payload`; on failure it prints git's stderr and the command exits `1`, as `_set_hooks_path` already does. This is the only index change the tool makes: no other path is staged and nothing is committed.
- Tests:
  - `test_the_installed_hook_is_executable` now reads the mode from `git ls-files -s` and runs on every platform.
  - The on-disk `0o755` assertion moved to `test_the_installed_hook_keeps_its_mode_on_disk`, which keeps the existing Windows skip because POSIX mode bits are not meaningful there.
  - `test_init_stages_only_the_hook_and_makes_no_commit` and `test_update_stages_only_the_hook_and_makes_no_commit` assert the staged set is exactly the hook and that `HEAD` does not exist.
  - `test_update_records_the_hook_mode_in_the_index` sets the entry back to `100644`, runs `update`, and asserts `100755`.
  - `tests/guardrail/support.py` gains `GitRepo.index_mode`, `GitRepo.staged_paths` and `GitRepo.has_commits`.
- `README.md`: the "What it creates" table records the index mode; the `init` paragraph names the `update-index --add --chmod=+x` step and the narrow exception to "the tool never stages or commits"; the `update` paragraph lists it; and the project-specific steps give the manual `git add --chmod=+x` step (plus the `update-index --add --chmod=+x` form for a Windows checkout) and the `git ls-files -s` check for a project-owned `.agents/hooks.local/pre-commit`.

### Verification

| Check | Result |
| --- | --- |
| `py -3.14 -m unittest discover -s tests -t .` with Git's `sh.exe` and Python 3.14 on `PATH` | 110 tests, 108 passed, 1 failed, 1 skipped |
| `PYTHONPATH=src py -3.14 -m agent_kit update` in this repo | `git ls-files -s .agents/kit/hooks/pre-commit` → `100755` |
| `git diff --cached --name-only` after that update | `.agents/kit/hooks/pre-commit` only |

The one failure is pre-existing and environmental, recorded in agent-kit/13-shared-test-support's review: `test_a_line_ending_change_only_is_not_a_local_change` fails because this clone has `core.autocrlf=true`, so the payload's `workflow.md` is CRLF on disk and the test's blind `replace(b"\n", b"\r\n")` turns it into CRCRLF. It fails identically at the base commit. The skip is the POSIX-only on-disk mode test on Windows. The same `PATH` workaround as ticket 13 was needed for `find_shell()` to find Git's `sh.exe` rather than the WSL `bash` stub.

