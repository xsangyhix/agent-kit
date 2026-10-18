Labels: ready-for-agent
Status: awaiting-agent

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
