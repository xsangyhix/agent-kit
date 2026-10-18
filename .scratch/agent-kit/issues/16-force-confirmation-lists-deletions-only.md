Labels: ready-for-human
Status: in-review

## Description

Found in the 2026-10-18 code review of the agent-kit effort. `update --force` passes every local change to `confirm_deletion`, including `AGENTS.md` when the kit block was edited or its markers are missing. So `AGENTS.md` is listed under "These paths will be deleted:", although update never deletes it: it only rewrites the block.

The user decided on 2026-10-18 during the review: list only the files that will really be deleted, and report a changed or missing kit block on a line of its own. This amends the confirmation text in design §8 and §9. Record the decision in `README.md`'s `--force` section, which is the kit's design record (`docs/agents/project.md`); do not edit the rc-machines design file.

Required output when there is an interactive terminal:

- Files to delete and a changed or missing block:
  ```
  These paths will be deleted:
  <path>
  ...
  The kit block in AGENTS.md will be replaced.
  Type 'yes' to delete them and continue: 
  ```
- Only the block changed (no file to delete): no "These paths will be deleted:" heading and no empty list:
  ```
  The kit block in AGENTS.md will be replaced.
  Type 'yes' to continue: 
  ```
- Only files: as today.

Unchanged:

- The non-interactive refusal (`Refusing --force: …`), printed before anything else.
- `yes` matching rules, the `Aborted. Nothing was changed.` message, and exit 1 on refusal.
- `init --force` output (it never touches the block during confirmation).
- The non-`--force` refusal list, which still names `AGENTS.md` with its reason: it lists changes, not deletions.

`confirm_deletion(paths, stdin, stdout)` keeps working with its current three arguments. If it needs to know about the block, add an optional keyword argument rather than changing the positional signature.

Test-Driven Development.

## Blocked by

- agent-kit/13-shared-test-support

## Acceptance criteria

- [ ] `update --force` with a modified kit file and an edited block prints the file under the heading, then the block line, then `Type 'yes' to delete them and continue: `.
- [ ] `update --force` with only an edited block (and with only missing markers) prints the block line and `Type 'yes' to continue: `, with no deletion heading.
- [ ] `AGENTS.md` never appears under "These paths will be deleted:".
- [ ] Non-interactive stdin still refuses with the existing message and changes nothing.
- [ ] `init --force` output is unchanged (existing tests pass).
- [ ] `README.md`'s `--force` section describes both forms.
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Check order on a broken block (agent-kit/14-init-force-checks-before-deleting).
- Any other wording change.

## Review

Implementation complete, submitted for review.

### Summary of changes

- `src/agent_kit/installer.py`: `confirm_deletion` gained an optional
  `replaces_block=False` keyword. Paths keep the current heading and prompt; a
  changed or missing block adds `The kit block in AGENTS.md will be replaced.`
  after them. With no paths, the heading is omitted and the prompt becomes
  `Type 'yes' to continue: `. `update --force` removes `AGENTS.md` from the
  deletion list and passes the block flag instead of listing it as a deletion.
  The positional signature and `init`'s call are unchanged.
- `tests/test_update.py`: four `--force` cases written first and seen fail
  against the old code: paths plus block, edited block only, missing markers
  only, and a declined block-only confirmation. The `edit_block` helper edits
  the block in place.
- `README.md`: the `--force` section now records both forms and states that
  `update` never deletes `AGENTS.md`.

### Verification

The four new tests failed before the change with `AGENTS.md` under the deletion
heading, then passed. Full suite:

```
py -3.14 -m unittest discover -s tests -t . -v
Ran 137 tests in 115.707s
OK (skipped=1)
```

The skip is the pre-existing Windows case, `test_the_installed_hook_keeps_its_mode_on_disk`.
`.agents/kit/check_tracker.py` exits 0.

### Judgement calls

- **Missing markers use the same line.** The ticket asks for the block line when
  the markers are missing, even though `update` appends a block there rather
  than replacing one; the wording follows the ticket verbatim.
- **Missing kit files stay in the deletion list.** The ticket is about
  `AGENTS.md`, which update never deletes. A missing kit-owned file sits under a
  folder that is removed and rewritten, so it is still listed; no other wording
  changed.

