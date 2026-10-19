Status: done

## Description

From the Standards axis of the 2026-10-18 code review of the agent-kit effort (Duplicated Code). In `tools/refresh_skills.py`, the `UPSTREAM` template hard-codes the line `excluded: skills/deprecated/, skills/engineering/setup-matt-pocock-skills/`. The script's own constants already say the same thing: `CATEGORIES` decides which category folders are copied, so it implicitly drops `skills/deprecated/`, and `EXCLUDED` names the excluded skill folder. If someone changes the constants, the `UPSTREAM` record silently goes wrong.

Build the `excluded:` line from one source of truth. One option is a single tuple of excluded paths that both the copy logic and the `UPSTREAM` text use. Keep the line's format and order exactly as design §10 specifies: `skills/deprecated/` first, each path with a trailing `/`, joined by `, `.

The output for today's constants must be byte-identical to `src/agent_kit/payload/skills/UPSTREAM`, apart from the `fetched:` date. Do not re-run the refresh against upstream as part of this ticket.

Test-Driven Development: first pin today's `UPSTREAM` text in `tests/test_refresh_skills.py`, if it is not already pinned. Then add a test proving that a changed exclusion list is reflected in the `excluded:` line.

## Blocked by

None.

## Acceptance criteria

- [x] The excluded paths are written down once in `tools/refresh_skills.py`.
- [x] The generated `UPSTREAM` for the current constants matches the committed file byte for byte, except the date. A test asserts it.
- [x] A test shows that a different exclusion list changes both what is copied and the `excluded:` line.
- [x] `src/agent_kit/payload/skills/` is unchanged.
- [x] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Refreshing the snapshot to a newer upstream commit.
- Any other change to the refresh tool.

## Review

Implementation complete, submitted for review.

### Summary of changes

`tools/refresh_skills.py`:

- `EXCLUDED` is now the single tuple of excluded paths: `skills/deprecated` and `skills/engineering/setup-matt-pocock-skills`.
- `excluded_line()` renders the `excluded:` value from that tuple: each path with a trailing `/`, joined by `, ` in tuple order.
- The `UPSTREAM` template takes `{excluded}` instead of hard-coded text.
- `build()` skips a category folder whose `skills/<name>` is in `EXCLUDED`; the `ignore` callback already handled nested exclusions and now reads the same tuple.

`tests/test_refresh_skills.py`:

- `test_generated_record_matches_the_committed_upstream_file` runs the tool against the synthetic archive and compares the generated record with `src/agent_kit/payload/skills/UPSTREAM`, replacing only the `fetched:` line with today's date.
- `test_excluded_tuple_drives_both_the_copy_and_the_record` appends a category (`skills/misc`) and a nested skill (`skills/productivity/grilling`) to `EXCLUDED`, then asserts neither is copied and both appear in the `excluded:` line in order.

The committed `UPSTREAM` text was already pinned by `test_snapshot_copies_the_four_categories_license_and_record`; the new test ties that text to the file on disk.

### Verification

TDD: `test_excluded_tuple_drives_both_the_copy_and_the_record` failed first (`AssertionError: True is not false` for `misc`), then passed after the implementation.

| Check | Result |
| --- | --- |
| `py -3.14 -m unittest tests.test_refresh_skills -v` | 9 tests, OK |
| `py -3.14 -m unittest discover -s tests -t . -v` | 168 tests, OK (skipped=1, the pre-existing Windows-only on-disk mode test) |
| `py -3.14 tools/check_payload_sync.py` | exit 0 |
| `git status` on `src/agent_kit/payload/skills/` | unchanged |

