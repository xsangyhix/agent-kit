Labels: ready-for-agent
Status: awaiting-agent

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

- [ ] `update` on a CRLF `AGENTS.md` (block present, and block missing so it is appended) leaves every byte outside the block identical, and writes the markers and block with CRLF.
- [ ] `init` on an existing CRLF `AGENTS.md` (with markers, and without) does the same.
- [ ] LF files behave exactly as before (the existing tests pass unchanged).
- [ ] A CRLF install followed by `update` with no changes reports no local changes (the block hash matches).
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Mixed line endings within one file beyond the rule above (the first line ending decides).
- Line endings of any other project-owned file; the kit only writes into `AGENTS.md` and appends to `.gitattributes`.
