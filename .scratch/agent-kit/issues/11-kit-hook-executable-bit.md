Labels: ready-for-agent
Status: awaiting-agent

## Description

**Where to work:** this repository, branch `agent/agent-kit`.

`agent-kit init` and `update` write `.agents/kit/hooks/pre-commit` with the right bytes and set mode `0o755` on disk (`installer._copy_payload`), but they never record that mode in the git index. On Windows (`core.filemode=false`) git records a newly added hook as `100644`, so a POSIX clone checks out a non-executable hook and git silently skips it: the agent-session `dev` gate, the `.scratch` gitignore check, the tracker check and the project's local hook all stop running with no warning.

Found 2026-10-18 (ticket 09 review, note 2). Ticket 09 worked around it only for its own project-owned hook, by hand.

Decided 2026-10-18 during the review: **the tool records the mode itself.** After `_copy_payload` chmods the hook, run `git -C <root> update-index --add --chmod=+x .agents/kit/hooks/pre-commit` in both `init` and `update` (`--add` covers a fresh install where the file is not yet indexed; on `update` it flips the bit on the already-tracked file). This amends design §8's "the tool never stages or commits" by the narrowest amount: it touches only the mode of the one hook file it just wrote, and never stages or commits anything else. Record the amendment in `README.md` (the kit's design record per `docs/agents/project.md`); do not edit the rc-machines `design.md`.

Test-Driven Development.

## Blocked by

- agent-kit/13-shared-test-support

## Acceptance criteria

- [ ] After `init` in a fresh repo, `git ls-files -s .agents/kit/hooks/pre-commit` reports mode `100755`; a test asserts it by reading the index, not the filesystem bit.
- [ ] After `update` over an existing install, the same check reports `100755`.
- [ ] The on-disk mode stays `0o755` (the existing assertion holds).
- [ ] `init` and `update` touch the index only for the hook path: `git status` shows no other file staged by the tool, and no commit is made.
- [ ] `test_the_installed_hook_is_executable` no longer skips on Windows, and it inspects the index.
- [ ] `README.md` records the index-mode step and the narrow exception to "never stages or commits", and gives the manual `git add --chmod=+x` step for a project-owned `.agents/hooks.local/pre-commit`.
- [ ] After the fix, `PYTHONPATH=src py -3.14 -m agent_kit update` in the agent-kit repo re-records its own `.agents/kit/hooks/pre-commit` as `100755`; the repo's `git ls-files -s` shows `100755` for that path after committing.
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Fixing the mode of project-owned `.agents/hooks.local/pre-commit` automatically: the tool never writes that file, so it is documented, not fixed.
- Making the protected branch configurable (design §13).
- A POSIX CI job that checks out the committed tree and proves the hook runs (no POSIX runner exists here); the index-mode test is the proxy.
- Taking the fix into rc-machines' installed copy; that is agent-kit/22-rc-machines-takes-the-kit-fixes.
