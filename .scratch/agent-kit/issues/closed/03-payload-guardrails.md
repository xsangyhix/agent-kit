Status: done

## Description

**Where to work:** `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`. Source files are read from rc-machines (`D:\Marcin\PycharmProjects\rc-machines`, branch `agent/agent-kit`). Ticket status changes go in rc-machines on `agent/agent-kit`.

Read `.scratch/agent-kit/design.md` (in rc-machines) first, sections 2, 6 and 11. This ticket moves the tracker checker and the pre-commit hook into the kit, with their tests. Work test-first: port the tests, change their paths, watch them fail, then make them pass.

1. **Checker.** Copy rc-machines `scripts/check_tracker.py` → `src/agent_kit/payload/kit/check_tracker.py`. Change only: the docstring's `scripts/hooks/pre-commit` → `.agents/kit/hooks/pre-commit`, its `docs/agents/workflow.md` → `.agents/kit/workflow.md`, its ADR references → `.agents/kit/adr/…`, and the final hint line → `See .agents/kit/workflow.md and .agents/kit/issue-tracker.md.` No rule changes. It must run on Python 3.14 (design §2; the 3.8 floor was replaced on 2026-10-18).
2. **Hook.** Write `src/agent_kit/payload/kit/hooks/pre-commit` to design §11, using rc-machines `scripts/hooks/pre-commit` steps 1–3 as the base. Keep its explanatory comments (they explain why detection is presence-only and fails open visibly); drop the rc-machines header comment and step 4 (release build). The header comment says: installed by agent-kit; `agent-kit init` sets `core.hooksPath`; project-specific steps go in `.agents/hooks.local/pre-commit`. LF line endings (check with `git ls-files --eol`). Commit it with the executable bit (`git update-index --chmod=+x`).
3. **Tests.** Port rc-machines `testing/guardrail_001/` (`support.py`, `test_check_tracker.py`, `test_pre_commit_hook.py`, `__init__.py`) to `tests/guardrail/`. Changes:
   - `support.py`: `REPO_ROOT` is the agent-kit root; `CHECKER = REPO_ROOT / "src/agent_kit/payload/kit/check_tracker.py"`; `HOOK = REPO_ROOT / "src/agent_kit/payload/kit/hooks/pre-commit"`. `add_hook_fixtures()` writes a no-op `.agents/kit/check_tracker.py` and `.agents/kit/harness.sh` containing `AGENT_MARKERS="AI_AGENT OPENCODE"`; it no longer writes `src/server/build_release.py`.
   - The interpreter test asserts each venv probe appears once and the hook contains `"$PYTHON" .agents/kit/check_tracker.py`.
   - Keep every existing case (the six checker rules, non-UTF-8, both rename cases, the six branch/marker cases).
4. **New tests** in `tests/guardrail/test_pre_commit_hook.py`:
   - local hook present and exiting 0 → hook exits 0, and the local hook ran (it writes a marker file; assert the file exists);
   - local hook exiting 3 → hook exits 3;
   - the local hook sees `PYTHON` and `branch` (it writes their values to a file; assert both non-empty and `branch` correct);
   - no local hook → hook exits 0;
   - `harness.sh` naming a custom marker (`AGENT_MARKERS="MY_AGENT"`): on `dev` with `MY_AGENT=1` → refused; with only `OPENCODE=1` → allowed;
   - `harness.sh` missing → the hook warns (assert the warning text) and still refuses `dev` with `OPENCODE=1`;
   - `PROTECTED_BRANCH=dev` appears on exactly one line of the hook.
   Run the hook with the `find_shell()` shell, as the existing tests do. In every test, clear all marker variables from the environment first (the test run may itself be an agent session).

## Blocked by

- `agent-kit/01-kit-repo-skeleton`

## Acceptance criteria

- [x] `py -3.14 -m unittest discover -s tests -t . -v` passes, and the hook tests ran rather than being skipped (state the shell that was found in the review summary).
- [x] Every ported test was seen failing before its path fix or implementation, and passing after (note it in the review summary).
- [x] The checker's rules and messages are unchanged except the final hint line.
- [x] The hook is LF, executable in the git index, and contains no `src/server`, `build_release` or `scripts/` reference.
- [x] The code targets Python 3.14 (design §2); the original 3.8 floor is superseded.

## Out of scope

- Generating `harness.sh` (ticket 06); here it is only a test fixture.
- Any change to the checker's rules (design §13).
- Removing the originals from rc-machines (ticket 09).

## Review

Implementation complete, submitted for review.

### Summary of changes

- `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`, commit `9231624`:
  - `src/agent_kit/payload/kit/check_tracker.py` — the checker copied from rc-machines; only the docstring paths and the final hint line changed, no rule or message.
  - `src/agent_kit/payload/kit/hooks/pre-commit` — the rc-machines hook's steps 1–3 plus design §11's marker loading, interpreter resolution and local-hook step; the rc header and the release build are gone. LF, mode `100755` in the index.
  - `tests/guardrail/` — `__init__.py`, `support.py`, `test_check_tracker.py`, `test_pre_commit_hook.py`; every ported case, the eight new cases this ticket lists, and one extra static check for the legacy-reference acceptance criterion.
- This ticket — the 3.8 references replaced with 3.14, status and label moved for review.

### Verification

| Check | Result |
| --- | --- |
| `py -3.14 -m unittest discover -s tests -t . -v` from agent-kit | 30 tests, OK, exit 0 |
| Shell found for the hook tests | `C:\Program Files\Git\usr\bin\sh.exe`; no skips |
| Red step, same command before the checker and hook existed | 26 guardrail tests failed (10 checker, 16 hook); the 4 CLI tests passed |
| Guardrail tests after implementation | 26 passed |
| `git ls-files --eol src/agent_kit/payload/kit/hooks/pre-commit` | `i/lf w/lf attr/text eol=lf` |
| `git ls-files -s src/agent_kit/payload/kit/hooks/pre-commit` | `100755` |
| Hook references to `src/server`, `build_release`, `scripts/` | none; the only `Scripts/` is `.venv/Scripts/python.exe`, which step 5 requires |
| Checker diff against `rc-machines/scripts/check_tracker.py` | docstring paths and the final hint line only |

### Notes for the reviewer

1. **Python floor.** The ticket still named 3.8, but design §2 was changed to 3.14 for every file on 2026-10-18 (ticket 01, Q9). I asked; the answer was 3.14 per design, and the description, the test command and the last acceptance criterion were updated to match.
2. **`python3` probe.** Design §11 says "`python3` on PATH", but this machine's `python3` is a Microsoft Store alias that prints "Python was not found" and exits non-zero. The hook probes `python3 --version` instead of `command -v python3`, so the broken alias falls through to `python`; a working `python3` is still preferred.
3. **Test PATH.** Git prepends its own bin folders to PATH when it runs a hook, which is how `sh .agents/hooks.local/pre-commit` resolves for a real commit. The tests launch the hook directly, so `support.run_hook()` prepends the shell's own folder to PATH to give the hook the same reach.
4. **Extra test.** `test_hook_has_no_project_specific_references` is the only test beyond the eight the ticket lists; it locks the corresponding acceptance criterion.
