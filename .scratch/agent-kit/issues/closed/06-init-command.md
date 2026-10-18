Status: done

## Description

**Where to work:** `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`. Ticket status changes go in rc-machines (`D:\Marcin\PycharmProjects\rc-machines`) on `agent/agent-kit`.

Read `.scratch/agent-kit/design.md` (in rc-machines) sections 4–8 first. **Design §8 is the specification for this ticket**; follow its checks, order of steps and messages exactly. Work test-first.

Implement:

1. `src/agent_kit/harness.py`: the table exactly as in design §6.
2. `src/agent_kit/lock.py`:
   - `file_hash(path) -> str` and `text_hash(text) -> str`, using the hash rule of design §7 (`\r\n` → `\n` before SHA-256);
   - `read_lock(root) -> dict or None` (None when the file is missing; raise `ValueError` with the path when it is not valid JSON or lacks a key);
   - `write_lock(root, kit_version, harness, files, agents_block_hash)` writing the format of design §7 (keys sorted, 2-space indent, trailing newline, POSIX paths).
3. `src/agent_kit/installer.py`:
   - `payload_root()` → `Path(__file__).parent / "payload"`.
   - `confirm_deletion(paths, stdin, stdout) -> bool`, exactly as design §8.
   - Kit block functions: `find_block(text)` returning the marker state (`"ok"` with the span, `"absent"`, or `"bad"` with a reason) and `apply_block(text, block) -> str`, implementing design §5. The block written between the markers is the content of `payload/agents-block.md` with its trailing newline normalised to exactly one, surrounded by one newline after the begin marker and before the end marker. The template's `{{KIT_BLOCK}}` placeholder is simply replaced by this step, because it sits between the markers.
   - `init(root, harness_name, force, stdin, stdout) -> int` implementing design §8.
4. `src/agent_kit/cli.py`: wire `init` to `installer.init` (pass `sys.stdin`, `sys.stdout`). Usage errors (design exit 2) are printed to stderr.

Tests in `tests/test_init.py`. Each test makes a throwaway git repo in a temp folder (reuse or copy the `GitRepo` helper from `tests/guardrail/support.py`) and calls `installer.init` directly, passing a fake stdin: a `io.StringIO` subclass whose `isatty()` returns what the test needs. Cover at least:

- fresh repo: kit files and skills copied byte for byte; `harness.sh` content; templates created; `AGENTS.md` block filled (no `{{KIT_BLOCK}}` left); `docs/adr/.gitkeep`, `.scratch/.gitkeep`; `.gitattributes` line; `git config core.hooksPath` equals `.agents/kit/hooks`; the lock lists every kit file with correct hashes, and `harness.sh`; exit 0;
- existing `GLOSSARY.md` and `docs/agents/project.md` are kept byte-identical and reported as kept;
- existing `AGENTS.md` without markers: the original text is kept and the block appended; with markers: only the block changes; with a bad marker state (only a begin marker): exit 1 and **nothing written** (no `.agents/kit/`, no lock);
- `.gitattributes` with the line already present: not duplicated;
- not a git root (a subfolder of a repo, and a plain folder): exit 2;
- unknown harness: exit 2;
- already installed (lock present): exit 2;
- conflict under `.agents/skills/` without `--force`: exit 1, the conflicting path printed, nothing written;
- conflict with `--force` and `isatty()` false: exit 1, the refusal message, the conflicting file still there;
- conflict with `--force`, `isatty()` true, answer `no`: exit 1, nothing changed;
- conflict with `--force`, `isatty()` true, answer `yes`: exit 0, the old file gone, the kit installed;
- a file under `.agents/hooks.local/` is never touched;
- running the installed hook (`.agents/kit/hooks/pre-commit` with the `find_shell()` shell) inside the freshly initialised repo on branch `agent/test` with a valid staged ticket exits 0. This proves the payload paths and `harness.sh` agree with the hook.

## Blocked by

- `agent-kit/03-payload-guardrails` — the hook and `harness.sh` contract.
- `agent-kit/04-payload-skills-snapshot` — the skills payload that init copies.
- `agent-kit/05-payload-project-templates` — the templates and the kit block.

## Acceptance criteria

- [x] Every behaviour in design §8 has a test, and the whole suite passes.
- [x] Nothing is written when any check fails (each refusal test asserts it).
- [x] `--force` can never delete without a `yes` typed at an interactive terminal.
- [x] Manual check, recorded in the review summary: in a new empty git repo in a temp folder, `python -m agent_kit init` (with `PYTHONPATH` pointing at `src`) installs the kit, and a `git commit` of the result on a branch `agent/test` runs the kit's hook and succeeds.
- [x] The code targets Python 3.14, as design §2 and `pyproject.toml` require (Q1).

## Out of scope

- `agent-kit update` (ticket 07).
- Staging or committing anything in the target project.
- Harnesses other than opencode.

## Questions

**Q1 - Python floor: 3.8 or 3.14?** The acceptance criteria say "No code uses a feature newer than Python 3.8", but design §2 says "every file targets **Python 3.14** (decided 2026-10-18, replacing the initial 3.8 floor)", and `pyproject.toml` already declares `requires-python = ">=3.14"`. Design §3 says a disagreement between a ticket and the design must be put to you rather than resolved by picking one. **Recommended:** follow the design — target Python 3.14 and rewrite the stale acceptance criterion to say so. **Answer:** accepted, 2026-10-18: target Python 3.14; the 3.8 acceptance criterion is stale and is rewritten below.

## Review

Implementation complete, submitted for review.

### Summary of changes

- `D:\Marcin\PycharmProjects\agent-kit`, branch `agent/agent-kit`: one commit, `bbe1eb7` — `feat: add the init command`.
  - `src/agent_kit/harness.py` — the harness table from design §6, verbatim.
  - `src/agent_kit/lock.py` — `file_hash`, `text_hash`, `read_lock` (missing → `None`; bad JSON or a missing key → `ValueError` naming the path) and `write_lock` (sorted keys, 2-space indent, trailing newline, POSIX paths).
  - `src/agent_kit/installer.py` — `payload_root()`, `confirm_deletion()`, `find_block()`/`apply_block()` and `init()` in the order design §8 gives.
  - `src/agent_kit/cli.py` — `init` wired to `installer.init` with `sys.stdin` and `sys.stdout`; `update` still returns 2.
  - `tests/test_init.py` — 42 tests: every design §8 behaviour plus the lock and block helpers.
  - `tests/test_cli.py` — the "init is not implemented" test is replaced by one that checks the wiring and the stderr usage error.
- This ticket — Q1 answered, acceptance criteria ticked, status and label moved for review.

### Verification

| Check | Result |
| --- | --- |
| `py -3.14 -m unittest tests.test_init -v` (red before the implementation, green after) | 42 tests, OK |
| `py -3.14 -m unittest discover -s tests -t . -v` | 85 tests, OK, exit 0 (1 skipped: POSIX mode bits on Windows) |
| Manual check — new empty repo, branch `agent/test`, `PYTHONPATH=src py -3.14 -m agent_kit init` | exit 0; 123 files installed; summary printed |
| Manual check — `git add -A && git commit -m "install agent kit"` | exit 0, commit `99592b7`; the installed hook ran and passed |
| Manual check — staged `.scratch/bad/issues/01-bad.md` with no `Status:` line, then commit | refused by `.agents/kit/check_tracker.py`, exit 1 — the installed hook really runs |
| Refusal tests | each asserts no `.agents/kit/`, no `kit.lock` and no `.gitattributes` after the refusal |
| `--force` confirmation | non-tty, `no`, and `yes` paths each tested; deletion happens only after `yes` |
| Python floor | code targets 3.14 per Q1; no 3.8 ceiling remains |

### Notes for the reviewer

1. **`find_block` returns a `BlockState(state, begin, end, reason)`.** For `"ok"`, `begin`/`end` are the indices where the two marker lines start; `apply_block` replaces that span. `"bad"` carries a reason naming the problem. Ticket 07 can reuse both.
2. **Streams.** Design exit-2 (usage) errors go to `sys.stderr`; refusals, the deletion dialogue and the summary go to the `stdout` argument. This matches the ticket's "usage errors printed to stderr" while keeping the injectable streams.
3. **`--force` deletes only the two kit-owned folders**, after the typed confirmation, and `.agents/hooks.local/` is outside both — the test pins that it is untouched.
4. **`.gitattributes` is append-only.** When the line is already present the file is left byte-identical; otherwise the line is appended, adding a leading newline only when the existing file lacks one.
5. **Templates are written from bytes**, so LF survives on Windows; the kit block is written with `newline="\n"`.
6. **`{{KIT_BLOCK}}` is replaced by the same `apply_block` call.** A freshly created `AGENTS.md` therefore reports "filled from the template"; an existing file reports "appended" or "replaced".
7. **The one skip** is the POSIX mode-bit assertion for the hook; Windows does not carry that bit. The hook still runs, as the manual commit above shows.
