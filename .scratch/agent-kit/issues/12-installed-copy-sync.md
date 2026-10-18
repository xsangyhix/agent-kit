Labels: ready-for-agent
Status: awaiting-agent

## Description

The agent-kit repo holds two copies of the same files: the **payload** under `src/agent_kit/payload/`, which is the source of truth, and the **installed copy** under `.agents/kit/` and `.agents/skills/`, which `agent-kit init`/`update` produce from it. `docs/agents/project.md` tells an agent to edit the payload, run `agent-kit update` and commit both, but nothing enforces it. Every test exercises `init`/`update` in a temporary repository, so none of them looks at this repo's own `.agents/` tree: a forgotten `update` leaves a stale installed copy and the suite stays green.

Found 2026-10-18 during ticket 10's review (note 3). The acceptance check there proved the two copies identical with an ad-hoc hash script kept outside the repo; that script is the seed of this ticket.

Two drift cases must be caught:

- a payload file edited without `agent-kit update` (the installed copy is stale);
- a version bump or `harness.py` edit that leaves the payload tree unchanged but makes generated output stale (`.agents/kit/harness.sh`, `kit_version` in the lock, the kit block in `AGENTS.md`).

The kit-owned hook cannot host the check: `.agents/kit/hooks/pre-commit` runs in every project, where no payload exists. This check is repo-local and project-owned.

### Where the check lives

- `tools/check_payload_sync.py`, a maintainer tool like `tools/refresh_skills.py`; it is **not** installed into projects and needs no packaging change. Standard library only.
- Its public surface is a deep module the tests can call:
  - `check(root, payload=None) -> list[str]` returns one line per problem; an empty list means in sync. `payload` defaults to `root / "src" / "agent_kit" / "payload"`, so tests can point it at a temporary copy.
  - `main() -> int` binds the roots to the repo layout, prints the problems, and returns `0` or `1`. The repo root is `Path(__file__).resolve().parents[1]`.
- The script must put `src/` on `sys.path` before importing `agent_kit`: the package is not installed in every checkout, and the hook must work without `PYTHONPATH` or `pip install -e .`.
- It writes nothing, stages nothing, and prints nothing on success. A hook that chatters on every commit trains people to ignore it.

The repo has no CI, so "on every commit" is enforced by a project-owned local hook, `.agents/hooks.local/pre-commit`:

```sh
#!/bin/sh
# Project-specific pre-commit step for agent-kit.
# The kit hook runs this last and exports PYTHON; see .agents/kit/hooks/pre-commit.
"${PYTHON:-python}" tools/check_payload_sync.py
```

The kit hook exports `PYTHON` (step 4 of `.agents/kit/hooks/pre-commit`), which is this repo's Python 3.14 `.venv` interpreter. `agent-kit update` never writes or deletes `.agents/hooks.local/`, so the hook survives updates.

### What it compares

Hashes come from `agent_kit.lock.file_hash`/`text_hash`, so CRLF and LF checkouts compare equal (design §7's hash rule).

1. **Payload trees.** Every file under `payload/kit/` must have an identical file under `.agents/kit/`, and every file under `payload/skills/` an identical one under `.agents/skills/`. Skip `__pycache__/` and `*.pyc` on both sides, as `installer._copy_tree` does.
2. **Generated extras.** Every file under `.agents/kit/` and `.agents/skills/` must have a counterpart in the payload, except `.agents/kit/harness.sh`. An extra file is reported; it is what the next `update` would delete.
3. **`harness.sh`.** Its bytes must equal `installer.HARNESS_SH.format(markers=...)` using the harness named in the lock. Read the harness from the lock, as the hook does, not from `DEFAULT_HARNESS`.
4. **The lock** (`agent_kit.lock.read_lock`):
   - `kit_version` equals `agent_kit.__version__`;
   - `harness` is a key of `HARNESSES`;
   - `files` has exactly the keys of the current kit-owned tree (kit, skills and `harness.sh`) with each hash matching `file_hash`.
5. **The kit block** in `AGENTS.md`: its text between the markers must equal `payload/agents-block.md` (normalised the way `installer._write_kit_block` writes it, i.e. content `rstrip("\n")`, one trailing newline), and the lock's `agents_block` must be that content's hash. Comparing the block to the **payload** is the point: comparing only to the lock would not notice an edited `agents-block.md` when `update` was never run, because the lock and `AGENTS.md` would still agree with each other.

### Failure behaviour

- Print a header, then `  - <path> (<reason>)` per problem, then the hint to run `agent-kit update` and commit the payload and the refreshed copy together. Reasons mirror `update`'s wording: `modified`, `missing`, `not in the payload`, plus the generated-output reasons above.
- Exit `1` when anything was reported, `0` otherwise.
- A missing `.agents/kit/` or `.agents/skills/` folder is reported **once** ("`.agents/kit/` is missing") and its per-file comparison is skipped, so a broken checkout produces one line, not a hundred.
- A missing payload folder, a missing or corrupt lock, and a missing or marker-broken `AGENTS.md` each produce one clear line; no traceback. Reuse `read_lock`'s `ValueError` message for a corrupt lock.
- If the lock names an unknown harness, report it and skip the `harness.sh` comparison (there are no markers to generate from).

### Tests

Test-Driven Development: write `tests/test_payload_sync.py` first, watch it fail, then implement. Use `tests.guardrail.support.GitRepo` plus `installer.init(...)` with a **copy** of the payload, so no test mutates the checkout. Cover at least:

- a clean install returns `[]`;
- one installed file edited, deleted, or added → the matching line and exit 1;
- one payload file edited after the install → `modified` (the core case);
- `harness.sh` overwritten → reported;
- a payload `agents-block.md` edited after the install → the block is reported;
- `kit_version` changed in the lock, and an unknown harness → reported;
- CRLF copies of both sides still return `[]`;
- `__pycache__`/`*.pyc` under the installed tree are ignored;
- a missing folder, a missing lock, a corrupt lock and marker-broken `AGENTS.md` each return one line and never raise;
- `main()` prints nothing and returns 0 when clean, prints the lines and returns 1 when drifted;
- the checker writes nothing: snapshot the tree (path, size, hash) before and after a drifted run and compare;
- an integration test that `check(REPO_ROOT) == []` for this repo;
- a subprocess run of `py -3.14 tools/check_payload_sync.py` from the repo root, asserting exit 0 and empty output, which proves the `sys.path` bootstrap works without an installed package.

Also add `.agents/hooks.local/* text eol=lf` to `.gitattributes`, record the hook's mode in the index with `git update-index --chmod=+x .agents/hooks.local/pre-commit` after staging, and verify `git ls-files -s` shows `100755` (ticket 11 is about the same problem for kit-owned hooks; this ticket only has to get its own project-owned hook right).

### Documentation

- `docs/agents/project.md`: name the sync check and the local hook in a sentence or two, so the next agent knows a green suite and a passing commit include it.
- `GLOSSARY.md`: add **Sync check** — a comparison that proves the installed copy, the lock and the kit block are what the current payload produces; this repo runs it on every commit and in the test suite.

## Blocked by

None.

## Acceptance criteria

- [ ] `py -3.14 tools/check_payload_sync.py` on the clean repo exits 0 and prints nothing.
- [ ] Every drift listed above is reported with the path and the reason, and exits 1: installed file modified, missing or extra; payload file edited after install; stale `harness.sh`; stale `kit_version`; unknown harness; block edited; `agents-block.md` edited after install.
- [ ] A CRLF checkout still passes, and `__pycache__`/`*.pyc` files are ignored.
- [ ] A missing installed folder, payload folder, lock, corrupt lock, missing `AGENTS.md` and marker-broken `AGENTS.md` each produce one line, with no traceback.
- [ ] A run with drift leaves the working tree byte-identical.
- [ ] `tests/test_payload_sync.py` covers the cases above and passes; the tests existed and failed before the implementation.
- [ ] `.agents/hooks.local/pre-commit` exists, is POSIX `sh` with LF, is `100755` in the git index, and refuses a commit while drift is present and allows a clean one (probe recorded in the review).
- [ ] `.gitattributes` contains `.agents/hooks.local/* text eol=lf`.
- [ ] `docs/agents/project.md` names the sync check and the local hook; `GLOSSARY.md` defines **Sync check**.
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.
- [ ] `py -3.14 -m agent_kit update` (with `PYTHONPATH=src`) still reports no local changes and exits 0 afterwards, and does not touch `.agents/hooks.local/`.

## Out of scope

- Running the check from the kit-owned `.agents/kit/hooks/pre-commit`, from `init`/`update`, or in another project. The kit hook sees no payload and must stay project-agnostic.
- CI; the repo has none.
- Checking project-owned files: `payload/templates/`, `docs/agents/project.md`, the rest of `.gitattributes`, `core.hooksPath`, `docs/adr/.gitkeep`, `.scratch/.gitkeep`.
- Fixing the executable-bit problem for installed hooks in general; that is `agent-kit/11-kit-hook-executable-bit` in rc-machines, still open. This ticket only records its own local hook's mode.
- Changing `agent-kit update`'s refusal behaviour or `--force`.
