Status: done

## Description

**Where to work:** create the new repo `D:\Marcin\PycharmProjects\agent-kit`. Ticket status changes go in rc-machines (`D:\Marcin\PycharmProjects\rc-machines`, branch `agent/agent-kit`).

Read `.scratch/agent-kit/design.md` (in rc-machines) first, sections 2, 3 and 12. This ticket creates the empty agent-kit repo with a working Python package skeleton, so later tickets only add content.

Steps:

1. Create the folder `D:\Marcin\PycharmProjects\agent-kit`. It must not exist yet; if it does, stop and ask the user.
2. `git init -b main`, then `git commit --allow-empty -m "chore: initial commit"` on `main`. This is the only commit any ticket makes on `main`.
3. `git branch dev`, then `git checkout -b agent/agent-kit dev`. All further work is on `agent/agent-kit`.
4. Create, following the layout in design §3:
   - `pyproject.toml`: build backend `setuptools.build_meta`, `requires = ["setuptools>=64"]`; project `name = "agent-kit"`, `version = "0.1.0"`, `requires-python = ">=3.14"`, no dependencies; `[project.scripts] agent-kit = "agent_kit.cli:main"`; `[tool.setuptools.packages.find] where = ["src"]`; `[tool.setuptools.package-data] agent_kit = ["payload/**/*"]`.
   - `src/agent_kit/__init__.py`: `__version__ = "0.1.0"`.
   - `src/agent_kit/__main__.py`: calls `sys.exit(main())` from `cli`.
   - `src/agent_kit/cli.py`: `main(argv=None) -> int` using `argparse` with `--version` (prints `agent-kit 0.1.0`) and two subcommands `init` and `update`, each accepting the arguments in design §8 and §9. For now both print "not implemented yet" to stderr and return 2. No subcommand → print help, return 2.
   - `src/agent_kit/payload/README.txt`: one line, "Files installed into projects. See design §3." (a placeholder so the folder exists; ticket 02 deletes it).
   - `tests/__init__.py`: inserts the absolute path of `src/` at the front of `sys.path`.
   - `tests/test_cli.py`: `--version` prints the version and returns 0; `init` and `update` return 2; no arguments returns 2. Call `cli.main([...])` directly and capture output with `contextlib.redirect_stdout`/`redirect_stderr`.
   - `.gitignore`: `__pycache__/`, `*.egg-info/`, `build/`, `dist/`, `.venv/`.
   - `.gitattributes`: `src/agent_kit/payload/kit/hooks/* text eol=lf` and `*.sh text eol=lf`.
   - `README.md`: a title and one paragraph saying what the kit is (from design §1). Ticket 08 writes the full README.
5. Commit on `agent/agent-kit`.

## Blocked by

None.

## Acceptance criteria

- [x] `D:\Marcin\PycharmProjects\agent-kit` is a git repo with branches `main` (one empty commit), `dev` (same commit) and `agent/agent-kit` (checked out, holding this ticket's commit).
- [x] `py -3.14 -m unittest discover -s tests -t . -v` passes from the repo root.
- [x] `py -3.14 -m agent_kit --version` (with `PYTHONPATH=src`) prints `agent-kit 0.1.0`.
- [x] `pip install -e .` in a throwaway 3.14 venv succeeds, and `agent-kit --version` then works. Delete that venv afterwards.
- [x] The package requires Python 3.14: `requires-python = ">=3.14"`, and no code targets an older version (design §2).

## Out of scope

- Any payload content (tickets 02–05), init/update logic (06, 07), the full README (08).
- A remote: the user adds GitLab later. Do not push.

## Questions

Grilling session recorded 2026-10-18, before implementation. Round 1 settled Q1, Q3, Q5, Q6, Q7 and Q8; round 2 settled Q4 and chose Python 3.14 for Q2; round 3 settled Q9. All questions are answered; implementation started 2026-10-18. Each question carries the answer I recommend, so an answer can accept it in a word. Facts found while preparing the questions are recorded with them, so no answer has to restate them.

**Q1 — How does step 2 create `main` on this machine?** The installed Git was 2.24.1.windows.2, which predates `git init -b` (added in 2.28). The user updated Git; it is now 2.56.0.windows.2, and I verified in a temp repo that `git init -b main` creates `main`. **Answer:** use step 2 exactly as written; no fallback is needed.

**Q2 — Which Python floor does the kit use?** Round 1 asked which interpreter verifies 3.8. The answer was a preference: use a newer Python when possible, and a question: what differs between 3.8 and 3.14? The decision that follows is the floor in `pyproject.toml` and design §2.

- Python 3.8 is out of support since October 2024; 3.14 is the current release. 3.8 receives no security fixes.
- Features this kit cannot use on 3.8: `match` and `X | Y` type unions (3.10), builtin generics such as `list[str]` in annotations evaluated at runtime (3.9), `str.removeprefix`/`removesuffix` and `dict | dict` (3.9), `importlib.resources.files` (3.9), `tomllib` (3.11), `except*` (3.11), PEP 695 `type` statements (3.12), and the 3.11+ performance work.
- The code this ticket writes needs none of them: `argparse`, `pathlib`, `sys` and `unittest` are enough. The cost of 3.8 is mostly typing style in a codebase that is still tiny.
- The floor exists because payload commands run under the project's interpreter: the hook resolves `.venv` or `python3` (design §11), so a project on 3.8 must be able to run `.agents/kit/check_tracker.py`. The CLI itself is installed separately with pipx, so its floor could be higher than the payload's.
- pipx here defaults to the system Python 3.8.1; a higher `requires-python` means installing with `pipx install --python 3.14 …`.

**Recommended:** keep `requires-python = ">=3.8"` and 3.8-compatible code for this ticket, and run the suite on both 3.8.1 and 3.14.6 (it should pass on both). This matches the ticket and design, and avoids a two-floor rule before the payload exists. The alternatives: split the floors — payload stays 3.8, the CLI package rises to 3.10 or 3.14 and may use modern syntax — or raise the whole kit. Either alternative amends design §2 and the last acceptance criterion. If you want a newer floor, say which version and whether it applies to the CLI only or to all files.

**Answer:** Python 3.14 chosen, 2026-10-18. The scope of the floor is Q9.

**Q3 — How is the throwaway venv built?** The 3.8 install carries pip 19.2.3 and setuptools 41.2.0, and a fresh venv inherits them; `pyproject.toml` requires `setuptools>=64`, so `pip install -e .` would fail before reaching our package. **Recommended:** create the venv under `C:\Users\marci\AppData\Local\Temp\opencode\agent-kit-01`, upgrade pip and setuptools inside it (leaving the system install untouched), run the editable install and `agent-kit --version`, then delete the venv. The alternative is to leave the tooling at 19.2.3 and lower the build requirement, which contradicts the ticket.

**Answer:** accepted, 2026-10-18: create the venv under the opencode temp folder and delete it after verification. With the 3.14 floor the venv inherits current pip and setuptools, so the upgrade is unnecessary.

**Q4 — How does the CLI return an exit code for `--version` and for no arguments?** Context: `src/agent_kit/cli.py` has a function `main(argv)` that reads the arguments and returns an exit code: 0 is success, 2 is a usage error. The tests call `main([...])` directly and compare the returned number. The standard library module `argparse` does two things that fight this. First, `--version` and `--help` print their text and then raise `SystemExit` — they stop the program instead of returning a number. Second, if we mark the subcommand as required, a run with no arguments prints only a one-line usage message and stops; the ticket asks for the full help. **Recommended:** build the parser with `prog="agent-kit"` and `action="version"`; in `main()`, catch `SystemExit` and return its code (0 when the code is `None`); do not mark the subcommand required; after parsing, if no subcommand is present, call `parser.print_help()` and return 2. Then `main(["--version"])` returns 0, `main(["--help"])` returns 0, and `main([])` prints the full help and returns 2. The alternative is to check for `--version` by hand before parsing; that is shorter, but `--help` still raises `SystemExit`, so the function would have two different behaviours.

**Answer:** accepted, 2026-10-18: catch `SystemExit`, return its code, print full help for no subcommand, return 2.

**Q5 — What exactly do the `init` and `update` stubs accept?** Design §8 and §9 define `init [--harness NAME] [--force] [PATH]` and `update [--force] [PATH]`. `harness.py` is not part of this ticket, so there is no harness table to validate against. **Answer:** accepted, 2026-10-18: opencode is the only harness now; the harness table is the seam for later harnesses, so ticket 01 accepts `--harness` as a free string (no `choices`) and ignores it. `PATH` is an optional positional defaulting to `"."`, `--force` is `store_true`; each stub prints `agent-kit: <command> is not implemented yet` to stderr and returns 2.

**Q6 — How much do the tests cover?** The ticket names four cases. **Recommended:** exactly those four in `tests/test_cli.py` — `--version` prints `agent-kit 0.1.0` and returns 0; `init` and `update` return 2 and print "not implemented yet" to stderr; no arguments returns 2 and prints help — capturing stdout and stderr as specified, and writing them first. No packaging test and no version-consistency test: ticket 08 owns packaging, and the `__version__`/`pyproject.toml` duplication is checked there. The alternative is a wider suite now.

**Answer:** accepted, 2026-10-18.

**Q7 — What does the README say?** Ticket 08 writes the full README; this ticket needs a title and one paragraph from design §1. **Recommended:** `# Agent kit` and one paragraph: the kit is the project-agnostic agent setup — workflow docs, tracker conventions, guardrails and the skill library — installed into any project, with `agent-kit init` to install it and `agent-kit update` to move to a newer version; rc-machines is its first user.

**Answer:** accepted, 2026-10-18.

**Q8 — What is the commit and verification trail?** **Recommended:** commit this question round in rc-machines as `docs: question ticket 01 before the agent-kit skeleton`; while working, set the ticket to `in-progress`, and record the answers here in the final submission commit; make exactly one agent-kit content commit, `feat: add package skeleton and CLI stubs`, on `agent/agent-kit` (plus the mandatory empty initial commit on `main`, which `dev` shares); then set `in-review`/`ready-for-human` and commit in rc-machines as `docs: submit ticket 01 for review`. Verification is the four acceptance commands on 3.14 plus the tracker check the pre-commit hook runs; rc-machines' `unittest` suite is not run because no rc-machines code changes. No push. The alternative is to commit the `in-progress` flip separately.

**Answer:** accepted, 2026-10-18.

**Q9 — Does the 3.14 floor cover every file, or only the CLI?** The package has two audiences. The CLI (`cli.py`, and later `installer.py`, `lock.py`, `harness.py`) is installed once with pipx and runs on the developer's machine. The payload (`payload/kit/check_tracker.py`, the hook, and later the copier) runs inside each project, under the interpreter the hook finds — `.venv` or `python3` (design §11). A project on 3.8 can run the payload only if the payload stays 3.8-compatible; `requires-python` does not protect it, because the payload is data, not an installed module. **Recommended:** split the floors. `pyproject.toml` gets `requires-python = ">=3.14"`, the CLI and tests use 3.14 freely, and `payload/**` stays 3.8-compatible, tested with a 3.8 run when ticket 03 adds payload code. Design §2 and the last acceptance criterion become a two-floor rule, and design §12 notes that pipx needs `--python 3.14` on this machine. The alternative is one 3.14 floor for every file: simpler, but a project on an older Python can no longer run the kit's checks.

**Answer:** B, 2026-10-18: one 3.14 floor for every file, including the payload. Design §2 and §12 and the acceptance criteria are updated; payload scripts must also run on 3.14.

## Review

Implementation complete, submitted for review.

### Summary of changes

- `D:\Marcin\PycharmProjects\agent-kit` — new git repo: `main` and `dev` at the empty initial commit `b5ff54d`; `agent/agent-kit` at `e11a0b8` with one content commit, `feat: add package skeleton and CLI stubs`.
- `pyproject.toml` — setuptools backend, `agent-kit 0.1.0`, `requires-python = ">=3.14"`, the `agent-kit` console script, `src` package discovery, and the payload package-data glob.
- `src/agent_kit/` — `__init__.py` (`__version__`), `__main__.py`, `cli.py` (the `argparse` surface: `--version`, `init`, `update`; both stubs return 2), and the `payload/README.txt` placeholder.
- `tests/` — `__init__.py` puts `src/` on `sys.path`; `test_cli.py` holds the four cases from Q6.
- `.gitignore`, `.gitattributes`, `README.md` — as specified in step 4; the README is the short version, ticket 08 owns the full one.
- `.scratch/agent-kit/design.md` — §2 and §12 updated for the 3.14 floor and `pipx install --python 3.14`.
- This ticket — the Python-floor questions, the answered Questions, and the acceptance criteria.

### Verification

| Check | Result |
| --- | --- |
| `py -3.14 -m unittest discover -s tests -t . -v` | 4 tests, OK |
| `PYTHONPATH=src py -3.14 -m agent_kit --version` | `agent-kit 0.1.0`, exit 0 |
| `py -3.14 -m agent_kit init` and `update` | `agent-kit: <command> is not implemented yet` on stderr, exit 2 |
| `py -3.14 -m agent_kit` | full help on stdout, exit 2 |
| `py -3.14 -m agent_kit --help` | help, exit 0 |
| Throwaway venv (`py -3.14 -m venv`), `pip install -e .`, `agent-kit --version` | install exit 0; `agent-kit 0.1.0`; venv deleted |
| `git -C D:\Marcin\PycharmProjects\agent-kit branch -vv` | `main` and `dev` at `b5ff54d`; `agent/agent-kit` at `e11a0b8` |
| `git -C D:\Marcin\PycharmProjects\agent-kit diff dev...HEAD --check` | clean |
| `python scripts/check_tracker.py` after staging this ticket | exit 0; the pre-commit hook runs it |

### Notes for the reviewer

1. **Python floor changed to 3.14.** Q2 chose 3.14 and Q9 chose one floor for every file. The ticket description, the last acceptance criterion, `design.md` §2 and §12 were updated to match. Payload scripts added by later tickets must therefore also run on 3.14. The system `python` is 3.8.1, so every command above names `py -3.14`, and pipx needs `--python 3.14`.
2. **Git was updated.** `git init -b main` (step 2) now works on Git 2.56.0; no fallback was needed.
3. **Pre-submission review.** A two-axis review of `git diff dev...HEAD` ran. It found no hard standards or spec violations. Its judgement calls were fixed: the duplicated `--force`/`path` definitions moved to `_add_common_arguments`; the parser builder is private (`_build_parser`); the unreachable exit-code branch is gone; the `unittest.main()` boilerplate is removed. One harmless addition remains: `description` and `readme` metadata in `pyproject.toml`.
4. **No push, no remote.** The user adds GitLab later.
