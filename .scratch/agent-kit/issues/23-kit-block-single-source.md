Labels: ready-for-agent
Status: awaiting-agent

## Description

A behaviour-preserving consolidation from the Standards axis of the 2026-10-18 code review of the agent-kit effort. It runs after agent-kit/18-installer-tidy, so it builds on the enum refactor there rather than colliding with it.

The kit block's hashed text is currently defined in three independent places:

- `installer._write_kit_block` returns `block + "\n"`;
- `installer._block_text` re-derives "content plus one trailing newline" from the text between the markers;
- `tests/test_init.py` pins the same `block_content() + "\n"` formula a third time.

A change to how the block's trailing newline or marker layout is written forces three coordinated edits (Shotgun Surgery). Give the block one canonical representation:

1. **One source for the hashed text.** Introduce a single function that returns the exact text the lock hashes (the `agents-block.md` content with CRLF normalised and the trailing newline normalised to exactly one), and make `_write_kit_block`, `_block_text` and `tests/test_init.py` all call it instead of re-expressing `block + "\n"`.
2. **Name the block-state classifier honestly.** `find_block` does not return the block; it classifies the marker state and returns a `BlockState`. Rename it (e.g. `classify_block`), and rename `_block_text` to say it returns the text the lock hashes.
3. **`block_action` is a bare string** (`"appended"`, `"filled from the template"`, `"replaced"`). Make it a small enum or named constants, matching what agent-kit/18 does for `BlockState.state`.

Behaviour and output must stay byte-identical for every command and outcome; the existing tests are the proof. If a name turns out not to be worth changing once in the code, leave it and say why in the review.

## Blocked by

- agent-kit/18-installer-tidy

## Acceptance criteria

- [ ] One function defines the text the lock hashes, and `_write_kit_block`, `_block_text` and `tests/test_init.py` use it rather than re-expressing `block + "\n"`.
- [ ] The marker-state classifier is renamed to reveal it returns a state, and `_block_text` is renamed to reveal it returns the hashed text.
- [ ] `block_action` uses an enum or named constants; no raw `"appended"` / `"filled from the template"` / `"replaced"` literals remain at call sites.
- [ ] No test that asserts output, exit codes or file contents changed. Tests that reached into a removed private name or string may be adapted.
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.
- [ ] `PYTHONPATH=src py -3.14 -m agent_kit update` in this repo still reports no local changes and exits 0.

## Out of scope

- Any change in behaviour or output wording.
- The CRLF line-ending handling of the block (agent-kit/15-agents-md-line-endings) or the whole-line marker rule (agent-kit/17-markers-on-their-own-line).
- `src/agent_kit/lock.py` beyond using its hash helpers.
