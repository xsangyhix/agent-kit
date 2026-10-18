Status: done

## Description

A spec bug found in the 2026-10-18 code review of the agent-kit effort. Design §8 says the checks are "all done **before anything is written**", and ticket 06 requires "Nothing is written when any check fails". `agent-kit init --force` breaks both rules: after the user types `yes`, it deletes `.agents/kit/` and the skills folder, and only then checks the kit block in `AGENTS.md`. If the block is broken, init refuses with exit 1 after the folders are already gone.

Reproduction from the review: a git repo with `.agents/skills/x/SKILL.md` and an `AGENTS.md` that has only a begin marker. `init --force`, answer `yes` → exit 1, `Cannot install: AGENTS.md has a broken agent-kit block…`, and `.agents/skills/x/SKILL.md` is deleted.

`update` gets the order right (confirm, then marker check, then delete), but it also asks for `yes` before refusing on a broken block. Fix both commands the same way: **run the marker check before the deletion confirmation**. That way nothing is deleted on a refusal, and the user is never asked to confirm a run that will then be refused.

Test-Driven Development: write the failing regression tests first.

## Blocked by

- agent-kit/13-shared-test-support

## Acceptance criteria

- [x] `init --force` with conflicting kit-owned files and a broken kit block exits 1, prints the broken-block message, does not prompt, and leaves the working tree byte-identical (snapshot before and after).
- [x] `update --force` with local changes and a broken kit block behaves the same way: exit 1, no prompt, nothing changed.
- [x] With a healthy block, the `--force` paths behave as before; the existing tests pass unchanged.
- [x] `README.md` still describes the behaviour correctly (update it if it states the order).
- [x] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Sharing the check sequence between `init` and `update`; that is agent-kit/18-installer-tidy.
- Any change to the confirmation text (agent-kit/16-force-confirmation-lists-deletions-only).

## Review

Implementation complete, submitted for review.

### Summary of changes

Both commands now run the marker check after the non-`--force` refusal list and
before the deletion confirmation. That is the smallest reordering that satisfies the
ticket: the existing non-`--force` output keeps its current order (a changed kit file
is still listed before a broken block is reported), and `--force` can no longer prompt
for a run it is about to refuse.

- `init`: `agents_path` and `state` are computed next to the conflict scan; the
  conflict refusal stays first; the broken-block refusal moved above
  `confirm_deletion`; the confirmation and the folder deletion follow it.
- `update`: the `if changes:` block became `if changes and not force:` for the
  refusal list, the broken-block refusal moved above the confirmation, and the
  confirmation kept its own `if changes:` block.
- `README.md`: the `--force` section now records that every check runs before the
  confirmation, so a refused run asks nothing and deletes nothing.
- `tests/guardrail/support.py`: `snapshot` moved there from `tests/test_update.py`,
  because `test_init.py` needs the same byte-for-byte comparison. Assertions were not
  changed; this follows ticket 13's rule that a helper with two users is shared.

### Verification

The two regression tests were written first and failed against the old code with the
prompt printed before the refusal:

```
These paths will be deleted:
.agents/skills/demo/SKILL.md
Type 'yes' to delete them and continue: Cannot install: AGENTS.md has a broken agent-kit block: ...
```

After the fix: 2 tests, 2 passed. Full suite: 114 tests, 113 passed, 1 skipped
(`test_the_installed_hook_keeps_its_mode_on_disk` skips on Windows, pre-existing).
`PYTHONPATH=src py -3.14 -m agent_kit update` reports no local changes and exits 0;
`.agents/kit/check_tracker.py` exits 0.

### Judgement calls

- **Refusal order for `init` without `--force`.** The conflict list still wins over a
  broken block, as before. Only the `--force` path needed to change, and keeping the
  old order keeps `test_a_conflict_without_force_is_refused_and_writes_nothing` and
  `test_an_edited_kit_block_is_refused_and_listed` untouched.
- **A broken block now beats the non-interactive `--force` refusal.** Both are exit 1,
  and the marker check is the more fundamental one; it is also what makes the
  confirmation skip unconditional.
