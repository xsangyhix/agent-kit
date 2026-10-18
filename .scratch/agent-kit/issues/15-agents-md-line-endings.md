Labels: ready-for-human
Status: in-review

## Description

A spec bug found in the 2026-10-18 code review of the agent-kit effort. Ticket 07 requires "No project-owned file changes on update (asserted byte for byte)", which includes the text of `AGENTS.md` outside the markers. Two things break this when `AGENTS.md` uses CRLF line endings:

- the installer reads the file with Python's universal newlines, which turns `\r\n` into `\n`;
- it writes the whole file back with LF only.

The review reproduced it: a CRLF `AGENTS.md` comes back from `update` as LF, with exit 0. `init` has the same problem when it writes the block into an existing CRLF `AGENTS.md`. With `core.autocrlf` git hides the diff, but without it the whole file shows as changed.

Required behaviour, for both `init` and `update`:

- Every byte of `AGENTS.md` outside the marker lines and the block is unchanged.
- The marker lines and the block use the file's line ending: CRLF if the file's first line ending is `\r\n`, otherwise LF. When the block is appended to a file that has no markers, the blank separator line uses that ending too.
- A new `AGENTS.md` created from the template keeps the template's bytes, as today.
- The `agents_block` hash in the lock is unaffected, because the hash rule already normalises CRLF. Write a test that proves it.
- `harness.sh`, the lock and `.gitattributes` keep their current LF output.

Test-Driven Development: write the failing byte-for-byte tests first.

## Blocked by

- agent-kit/13-shared-test-support

## Acceptance criteria

- [x] `update` on a CRLF `AGENTS.md` (block present, and block missing so it is appended) leaves every byte outside the block identical, and writes the markers and block with CRLF.
- [x] `init` on an existing CRLF `AGENTS.md` (with markers, and without) does the same.
- [x] LF files behave exactly as before (the existing tests pass unchanged).
- [x] A CRLF install followed by `update` with no changes reports no local changes (the block hash matches).
- [x] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Mixed line endings within one file beyond the rule above (the first line ending decides).
- Line endings of any other project-owned file; the kit only writes into `AGENTS.md` and appends to `.gitattributes`.

## Review

Implementation complete, submitted for review.

### Summary of changes

All changes are in `src/agent_kit/installer.py`:

- `_read_text` now reads the raw bytes and decodes without Python's universal-newline translation, so the installer sees `AGENTS.md` exactly as it is on disk.
- `apply_block` detects the file's line ending (`_line_ending`: CRLF when the first newline is a `\r\n`, otherwise LF) and writes the marker lines and the block with that ending. When the block is appended to a file with no markers, the blank separator line uses the same ending.
- `_write_kit_block` normalises the `agents-block.md` content to LF before hashing and before `apply_block` re-encodes it in the target file's ending. The template itself can be CRLF on a Windows checkout (`core.autocrlf=true`), so this keeps the `agents_block` lock hash stable and the written block correct.

The lock hash needed no change: `lock.text_hash`/`file_hash` already normalise CRLF, and `_block_text` already strips a leading `\r\n`. A test proves it (below). `harness.sh`, the lock and `.gitattributes` still keep their LF output; none of them is read or written through `_read_text`.

### Verification

Seven byte-for-byte tests were written first and failed against the old code — a CRLF `AGENTS.md` came back LF, losing its line endings:

- `BlockTests`: `apply_block` keeps a CRLF file CRLF, appends to a CRLF file with CRLF separators, and falls back to LF when the file has no newline.
- `InitTests`: `init` into a CRLF `AGENTS.md` (markers present, and absent) writes the block with CRLF and leaves every other byte identical.
- `UpdateTests`: `update` on a CRLF `AGENTS.md` (markers present, and absent) does the same, and a CRLF install followed by an unchanged `update` exits 0 — the block hash matches, so no local change is reported.

Full suite: `py -3.14 -m unittest discover -s tests -t . -v` — 121 tests, 120 passed, 1 skipped (`test_the_installed_hook_keeps_its_mode_on_disk`, the pre-existing POSIX-only skip on Windows). The suite held 114 tests before this ticket; the 7 above were added.

### Judgement calls

- **The first newline decides.** Per the ticket, `_line_ending` looks only at the first `\n` and whether it is preceded by `\r`; mixed endings within a file are out of scope.
- **`_read_text` is now byte-preserving for every caller.** Its only callers read `AGENTS.md` and the block template, both of which want the raw bytes; `harness.sh` and the lock are written elsewhere and keep LF.
- **Normalise the block template at the read site, not in `apply_block`.** `apply_block` already normalises any `\r\n` in its input, but the lone `\r` left by a naive `rstrip("\n")` on a CRLF template would survive into the written block, so the read site converts to LF first. This is also the single source ticket 23 will later extract.
