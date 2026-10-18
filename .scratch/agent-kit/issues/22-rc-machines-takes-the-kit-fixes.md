Labels: ready-for-agent
Status: awaiting-agent

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

- [ ] `update` exited 0. `.agents/kit/` matches the agent-kit payload at the recorded commit, and `.agents/kit.lock` matches the installed files.
- [ ] `AGENTS.md` changed only between the markers, if at all. `GLOSSARY.md`, `docs/agents/project.md` and `.agents/hooks.local/` were not touched by the tool.
- [ ] `.agents/hooks.local/pre-commit` uses `$PROTECTED_BRANCH`, is LF only, and is `100755` in the index.
- [ ] A probe commit on `agent/agent-kit` passes the hook and does not run the release build. The review records the hook output.
- [ ] The host-side suite passes: `python -m unittest discover -s testing -t . -v`.

## Out of scope

- The kit hook's executable bit in the index (agent-kit/11-kit-hook-executable-bit).
- Committing on `dev`. The release build path is only exercised by the user.
