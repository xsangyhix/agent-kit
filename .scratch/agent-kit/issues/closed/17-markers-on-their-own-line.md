Status: done

## Description

Found in the 2026-10-18 code review of the agent-kit effort. `installer.find_block` counts marker **substrings**, so an `AGENTS.md` that only *mentions* a marker in its prose, e.g. `` `<!-- agent-kit:begin -->` ``, is reported as a broken block, and `init` and `update` refuse ("found 1 begin and 0 end"). The refusal is safe but surprising, and a project documenting the kit in its own `AGENTS.md` cannot get past it.

The user decided on 2026-10-18 during the review: a marker counts only when it stands on a line of its own. This amends design §5's marker rules. Record the rule in `README.md` (the kit's design record per `docs/agents/project.md`); do not edit the rc-machines design file.

The rule:

- A line is a begin (end) marker when the line, with trailing whitespace and a trailing `\r` removed, equals `<!-- agent-kit:begin -->` (`<!-- agent-kit:end -->`) exactly. Leading whitespace means it is *not* a marker.
- Counting, the "one each, begin before end" check, and the refusal messages of §5 apply to marker lines only.
- Text between the marker lines is the block, as today; the lock's `agents_block` hash rule does not change.
- Marker text inside a line of prose, or indented, is ordinary text: it is preserved outside the block and never counted.

Backwards compatibility: every `AGENTS.md` the kit has written has its markers on their own lines, so existing installs (rc-machines, this repo) are unaffected. Prove it by running `update` against this repo with no local changes.

Test-Driven Development.

## Blocked by

- agent-kit/13-shared-test-support

## Acceptance criteria

- [x] An `AGENTS.md` mentioning a marker inline (and indented) with no real block: `init` appends the block and exits 0; the mention is preserved byte for byte.
- [x] The same mention alongside a real block: `init` and `update` replace only the real block.
- [x] One-only, duplicate and end-before-begin marker *lines* still refuse with exit 1 and the existing messages.
- [x] A marker line with trailing spaces or a CRLF ending still counts.
- [x] `PYTHONPATH=src py -3.14 -m agent_kit update` in this repo reports no local changes.
- [x] `README.md` states the whole-line rule.
- [x] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Changing the marker strings.
- Line-ending handling of the written block (agent-kit/15-agents-md-line-endings).

## Review

Implementation complete, submitted for review.

### Summary of changes

`src/agent_kit/installer.py`:

- `find_block` now scans lines through `_marker_lines`. A line counts as a begin or end marker only when its content, with trailing whitespace and a trailing `\r` removed, equals the marker exactly. The counting, the one-each check, the begin-before-end check and the refusal messages are unchanged; the counts now come from marker lines.
- `apply_block` ends the replaced span at `_line_content_end(text, state.end)` rather than after the end-marker text, so a real marker line's trailing whitespace is dropped and the marker lines are rewritten canonically. Bytes outside the marker lines are still preserved, including inline mentions.
- `_block_text` takes the text strictly between the marker lines (after the newline ending the begin line, up to the start of the end line). For canonical marker lines this is byte-identical to the old result, so the lock's `agents_block` hash rule is untouched; the change only makes trailing whitespace on marker lines irrelevant to the hash.
- `README.md` gains a "The kit block" section recording the whole-line rule, the leading/trailing-whitespace behaviour, CRLF tolerance, canonical rewriting and that inline/indented mentions are ordinary project text.

### Verification

Twelve tests were written first and failed against the old code:

- `BlockTests`: an inline mention is not a marker; a mention beside a real block reports only the real block; trailing whitespace on marker lines still counts; a marker in the middle of a line is not a marker; `apply_block` rewrites marker lines canonically and preserves an inline mention.
- `InitTests`: an inline/indented mention with no real block is preserved while the block is appended; a mention beside a real block leaves only the real block replaced; trailing-space marker lines are normalised; CRLF marker lines with trailing whitespace still count.
- `UpdateTests`: an inline mention is preserved while `update` replaces the real block; marker lines with trailing spaces report no local change and are normalised.

Full suite: `py -3.14 -m unittest discover -s tests -t . -v` — 133 tests, 132 passed, 1 skipped (`test_the_installed_hook_keeps_its_mode_on_disk`, the pre-existing POSIX-only skip on Windows). The suite held 121 tests before this ticket; the 12 above were added.

`PYTHONPATH=src py -3.14 -m agent_kit update` exits 0 and leaves `AGENTS.md` unchanged in git, so every existing install keeps its block hash.

### Judgement calls

- **Marker lines are canonicalised.** Trailing whitespace on a real marker line is tolerated on read but dropped on write, as settled in the grill: the marker lines are kit-owned, and keeping invisible bytes there would make the hashed block depend on them.
- **`state.begin`/`state.end` still point at the marker text**, so the existing span test and callers keep their meaning; the line boundaries are derived in `apply_block` and `_block_text`.
- **No marker lines means absent**, even when the file mentions markers in prose. That keeps `init` appending and `update` refusing with "kit block missing markers", which are the existing behaviours for a blockless file.
