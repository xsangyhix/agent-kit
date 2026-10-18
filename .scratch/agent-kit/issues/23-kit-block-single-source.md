Labels: ready-for-human
Status: in-review

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

- [x] One function defines the text the lock hashes, and `_write_kit_block`, `_block_text` and `tests/test_init.py` use it rather than re-expressing `block + "\n"`.
- [x] The marker-state classifier is renamed to reveal it returns a state, and `_block_text` is renamed to reveal it returns the hashed text.
- [x] `block_action` uses an enum or named constants; no raw `"appended"` / `"filled from the template"` / `"replaced"` literals remain at call sites.
- [x] No test that asserts output, exit codes or file contents changed. Tests that reached into a removed private name or string may be adapted.
- [x] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.
- [x] `PYTHONPATH=src py -3.14 -m agent_kit update` in this repo still reports no local changes and exits 0.

## Out of scope

- Any change in behaviour or output wording.
- The CRLF line-ending handling of the block (agent-kit/15-agents-md-line-endings) or the whole-line marker rule (agent-kit/17-markers-on-their-own-line).
- `src/agent_kit/lock.py` beyond using its hash helpers.

## Review

Implementation complete, submitted for review.

### Summary of changes

`src/agent_kit/installer.py`:

- **One source for the hashed text.** `canonical_block_text(block)` normalises CRLF to LF, strips every trailing newline and appends exactly one. `_write_kit_block` returns it, `_block_text_for_hash` (formerly `_block_text`) extracts the text between the marker lines and runs it through the same function, and `apply_block` now derives its written content from it too, so the normalisation exists once.
- **Honest names.** `find_block` is now `classify_block`, because it returns a `BlockState`; `_block_text` is now `_block_text_for_hash`, because it returns the text the lock hashes.
- **`block_action` is an enum.** `BlockAction` holds `APPENDED`, `FILLED_FROM_TEMPLATE` and `REPLACED`, with the existing report wording as their values. `_print_report` prints `block_action.value`; no raw action strings remain at call sites.

`tests/test_init.py` and `tests/test_update.py`:

- The lock-hash assertions use `installer.canonical_block_text(block_content())` instead of `block_content() + "\n"`. `test_update.py` held a fourth copy of that formula beyond the three the ticket named, so it was consolidated too.
- `BlockTests` calls `installer.classify_block` and gains one direct test of `canonical_block_text` covering CRLF and the trailing newline. No assertion on command output, exit codes or installed file contents changed.

### Verification

TDD: the renamed test assertions failed first against the old API (`AttributeError: module 'agent_kit.installer' has no attribute 'classify_block'`, then `canonical_block_text`), and passed once the installer changed.

```
py -3.14 -m unittest discover -s tests -t . -v
Ran 138 tests in 135.121s

OK (skipped=1)
```

The skip is the pre-existing Windows case, `test_the_installed_hook_keeps_its_mode_on_disk`; the packaging test ran and passed. The count is one higher than agent-kit/18 because of the new `canonical_block_text` test.

`PYTHONPATH=src py -3.14 -m agent_kit update` exits 0, reports no local changes, and leaves the installed copy untouched.

### Judgement calls

- **`canonical_block_text` is public, not private.** The tests must construct the same text the lock hashes, so the function they call is the production one rather than a test-side reimplementation.
- **`apply_block` uses the canonical function as well.** The ticket named `_write_kit_block`, `_block_text` and the test, but `apply_block` held the same CRLF/trailing-newline normalisation. Deriving its content from `canonical_block_text(...).removesuffix("\n")` removes the last copy without changing any written bytes; the existing CRLF and append tests pass unchanged.
- **`_block_text_for_hash` canonicalises the extracted text.** For a normal block that is idempotent. It also makes an empty block hash as `"\n"`, matching what `_write_kit_block` records for an empty payload; previously the two sides could only agree on a non-empty block. No command's output changes.
- **`BlockAction.FILLED_FROM_TEMPLATE` rather than `FILLED`.** The member name carries the full action, while its value preserves the exact report wording.
