Labels: ready-for-agent
Status: awaiting-agent

## Description

A spec bug found in the 2026-10-18 code review of the agent-kit effort. Design §8 says the checks are "all done **before anything is written**", and ticket 06 requires "Nothing is written when any check fails". `agent-kit init --force` breaks both rules: after the user types `yes`, it deletes `.agents/kit/` and the skills folder, and only then checks the kit block in `AGENTS.md`. If the block is broken, init refuses with exit 1 after the folders are already gone.

Reproduction from the review: a git repo with `.agents/skills/x/SKILL.md` and an `AGENTS.md` that has only a begin marker. `init --force`, answer `yes` → exit 1, `Cannot install: AGENTS.md has a broken agent-kit block…`, and `.agents/skills/x/SKILL.md` is deleted.

`update` gets the order right (confirm, then marker check, then delete), but it also asks for `yes` before refusing on a broken block. Fix both commands the same way: **run the marker check before the deletion confirmation**. That way nothing is deleted on a refusal, and the user is never asked to confirm a run that will then be refused.

Test-Driven Development: write the failing regression tests first.

## Blocked by

- agent-kit/13-shared-test-support

## Acceptance criteria

- [ ] `init --force` with conflicting kit-owned files and a broken kit block exits 1, prints the broken-block message, does not prompt, and leaves the working tree byte-identical (snapshot before and after).
- [ ] `update --force` with local changes and a broken kit block behaves the same way: exit 1, no prompt, nothing changed.
- [ ] With a healthy block, the `--force` paths behave as before; the existing tests pass unchanged.
- [ ] `README.md` still describes the behaviour correctly (update it if it states the order).
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Sharing the check sequence between `init` and `update`; that is agent-kit/18-installer-tidy.
- Any change to the confirmation text (agent-kit/16-force-confirmation-lists-deletions-only).
