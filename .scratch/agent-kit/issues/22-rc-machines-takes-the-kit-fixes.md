Labels: ready-for-human
Status: in-review

## Description

Bring the fixes from the 2026-10-18 code review of the agent-kit effort into rc-machines. Tickets 14–17, 19 and 21 change the agent-kit tool or its payload; rc-machines still carries the kit as installed in ticket 09.

Where to work: rc-machines (`D:\Marcin\PycharmProjects\rc-machines`), on `agent/agent-kit`. Do not commit in the agent-kit repo.

1. Run the update from the agent-kit working tree. The tool may not be installed with pipx yet, and design §12 allows this form:
   ```
   $env:PYTHONPATH = "D:\Marcin\PycharmProjects\agent-kit\src"
   py -3.14 -m agent_kit update D:\Marcin\PycharmProjects\rc-machines
   ```
   Record in the review which agent-kit commit you ran (`git -C D:\Marcin\PycharmProjects\agent-kit rev-parse HEAD`). The kit version stays `0.1.0`: the user bumps and tags versions at release, not in tickets.
2. If `update` refuses because of local changes, stop and ask. Do not use `--force`; it cannot run in an agent session anyway.
3. In `.agents/hooks.local/pre-commit`, replace the hard-coded `"dev"` in the branch test with `"$PROTECTED_BRANCH"`, which the kit hook now exports (agent-kit/21-hook-probe-note-and-protected-branch). Update the file's header comment, which lists the exported variables.
4. Keep `.agents/hooks.local/pre-commit` at mode `100755` in the index (`git ls-files -s`). If staging resets it, run `git update-index --chmod=+x` again, as ticket 09 did.

## Blocked by

- agent-kit/14-init-force-checks-before-deleting
- agent-kit/15-agents-md-line-endings
- agent-kit/16-force-confirmation-lists-deletions-only
- agent-kit/17-markers-on-their-own-line
- agent-kit/19-tracker-checker-tidy
- agent-kit/21-hook-probe-note-and-protected-branch

All of these live in the agent-kit repo, under `.scratch/agent-kit/issues/`.

## Acceptance criteria

- [x] `update` exited 0. `.agents/kit/` matches the agent-kit payload at the recorded commit, and `.agents/kit.lock` matches the installed files.
- [x] `AGENTS.md` changed only between the markers, if at all. `GLOSSARY.md`, `docs/agents/project.md` and `.agents/hooks.local/` were not touched by the tool.
- [x] `.agents/hooks.local/pre-commit` uses `$PROTECTED_BRANCH`, is LF only, and is `100755` in the index.
- [x] A probe commit on `agent/agent-kit` passes the hook and does not run the release build. The review records the hook output.
- [x] The host-side suite passes: `python -m unittest discover -s testing -t . -v`.

## Out of scope

- The kit hook's executable bit in the index (agent-kit/11-kit-hook-executable-bit).
- Committing on `dev`. The release build path is only exercised by the user.

## Review

Implementation complete, submitted for review.

### Summary of changes

Worked in `D:\Marcin\PycharmProjects\rc-machines` on `agent/agent-kit`. The agent-kit repo was not committed to.

- **Agent-kit commit run:** `73bbc01c9f803c61e8dc1cc68435976f8ea92b35` (`agent/agent-kit`, clean tree). Kit version stayed `0.1.0`.
- **`agent-kit update`** exited 0:
  - Updated `.agents/kit/GLOSSARY.md`, `.agents/kit/check_tracker.py`, `.agents/kit/hooks/pre-commit`, `.agents/kit/workflow.md`.
  - Added `.agents/kit/adr/0007-grill-before-pickup.md`.
  - Reported `Kit block: replaced in AGENTS.md`; its content was already identical, so `AGENTS.md` has no diff.
  - Recorded the installed kit hook's executable bit in the index (`100644` → `100755`, the agent-kit/11 fix). This is the out-of-scope item, but the update makes the change by design.
- **rc-machines commits:**
  - `b61f792` — `chore: take the agent-kit review fixes into rc-machines` (`.agents/kit/` and `.agents/kit.lock`).
  - `0ae11fe` — `chore: use the exported protected branch in the local hook`. `.agents/hooks.local/pre-commit` now tests `"$branch" != "$PROTECTED_BRANCH"`; its header comment names `PYTHON`, `branch` and `PROTECTED_BRANCH`.

### Verification

| Check | Result |
| --- | --- |
| `agent-kit update D:\Marcin\PycharmProjects\rc-machines` | exit 0; changed only kit-owned files |
| Installed `.agents/kit` and `.agents/skills` against `src/agent_kit/payload` | every payload file identical; only extra file is the generated `.agents/kit/harness.sh` |
| `.agents/kit.lock` against installed files | all hashes match; `agents_block` hash matches the `AGENTS.md` block |
| Before/after SHA-256 of `GLOSSARY.md`, `docs/agents/project.md`, `AGENTS.md` | unchanged; `.agents/hooks.local/pre-commit` changed only by this ticket's edit |
| `git ls-files -s .agents/hooks.local/pre-commit` | `100755` |
| `git ls-files -s .agents/kit/hooks/pre-commit` | `100755` |
| CR bytes in both hook files | 0; both end with LF |
| `sh -n .agents/hooks.local/pre-commit` | exit 0 |
| Host-side suite: `.\.venv\Scripts\python.exe -m unittest discover -s testing -t . -v` | 79 tests, OK, exit 0 |
| `git status` on `agent/agent-kit` after the commits | clean; no `src/server/public/` changes |

### Probe commit

`GIT_TRACE=1 git commit` for `0ae11fe` shows the hook running:

```
run-command.c:673       trace: run_command: GIT_EDITOR=: GIT_INDEX_FILE=.git/index .agents/kit/hooks/pre-commit
run-command.c:945       trace: start_command: .agents/kit/hooks/pre-commit
```

It exited 0 and printed no build output. Running the kit hook with `sh -x` shows the protected branch being handed to the local hook:

```
+ branch=agent/agent-kit
+ PROTECTED_BRANCH=dev
+ '[' agent/agent-kit = dev ']'
+ ./.venv/Scripts/python.exe .agents/kit/check_tracker.py
+ export PYTHON branch PROTECTED_BRANCH
+ sh .agents/hooks.local/pre-commit
+ local_status=0
```

And the local hook with the exported variables:

```
+ '[' agent/agent-kit '!=' dev ']'
+ exit 0
```

So on `agent/agent-kit` the release build is skipped; the `dev` path remains for the user to exercise on their next release commit, as ticket 09 noted.

