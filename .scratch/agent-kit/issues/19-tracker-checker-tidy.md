Labels: ready-for-human
Status: in-review

## Description

A behaviour-preserving cleanup of the tracker checker, `src/agent_kit/payload/kit/check_tracker.py`, from the Standards axis of the 2026-10-18 code review of the agent-kit effort:

1. **Duplicated code.** `parse_header` runs the same regex-match block twice, once for `Status:` and once for `Labels:`. Extract one helper that reads a named header field.
2. **Mysterious name.** `labels` holds exactly one label (the checker rejects anything that is not a single canonical label). Rename it `label` in `parse_header`, `check` and `main`. Keep the words "label" and `Labels:` in the user-facing messages unchanged.
3. **Style.** `if not UNIT_MARKER in name` → `if UNIT_MARKER not in name`.

The checker is payload, and it runs in every project's pre-commit hook. Its messages and exit codes must stay byte-identical. It must stay a standalone, stdlib-only script that runs on Python 3.14 with no import from `agent_kit`.

This changes the payload, so follow `docs/agents/project.md`: run `PYTHONPATH=src py -3.14 -m agent_kit update` to refresh this repo's installed copy (`.agents/kit/check_tracker.py` and the lock), and commit both.

## Blocked by

None.

## Acceptance criteria

- [x] The three items are done.
- [x] `tests/guardrail/test_check_tracker.py` passes unchanged. If it reaches into a renamed parameter, adapt only that.
- [x] `.agents/kit/check_tracker.py` is identical to the payload, and `.agents/kit.lock` matches (the `update` run exits 0).
- [x] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- New tracker rules, or support for more than one label.
- Taking the change into rc-machines (agent-kit/22-rc-machines-takes-the-kit-fixes).

## Review

Implementation complete, submitted for review.

### Summary of changes

`src/agent_kit/payload/kit/check_tracker.py`:

- **Duplicated code.** `read_header_field(lines, field)` extracts one named header field with a single regex; `parse_header` calls it twice. Both fields still take their first match within the first `HEADER_LINES` lines.
- **Mysterious name.** `labels` is now `label` in `parse_header`, `check` and `main`. The words "label" and `Labels:` in the user-facing messages are unchanged.
- **Style.** `if not UNIT_MARKER in name` is now `if UNIT_MARKER not in name`.

`.agents/kit/check_tracker.py` and `.agents/kit.lock` were refreshed with `PYTHONPATH=src py -3.14 -m agent_kit update`.

### Verification

TDD: the existing `tests/guardrail/test_check_tracker.py` suite is the safety net for a behaviour-preserving refactor. It was green before and after and needed no adaptation — it does not reach into `parse_header` or the renamed parameter.

- `py -3.14 -m unittest tests.guardrail.test_check_tracker -v`: 10 tests, OK, before and after.
- Differential run of the committed (`HEAD`) checker and the new one against 14 fixtures (valid tickets, missing/unknown status, unknown label, closed/active violations, duplicate fields, a field beyond `HEADER_LINES`, non-UTF-8, a non-unit doc): return code, stdout and stderr are byte-identical.
- `py -3.14 -m unittest discover -s tests -t . -v`: 165 tests, OK (skipped=1). The skip is the pre-existing Windows-only on-disk mode test.
- `PYTHONPATH=src py -3.14 -m agent_kit update` exits 0, and `.agents/kit/check_tracker.py` is identical to the payload.
- `py -3.14 tools/check_payload_sync.py` exits 0.

### Judgement calls

- **The helper takes the header lines, not the raw text.** `parse_header` slices to `HEADER_LINES` once and passes the lines, so the limit lives in one place. `read_header_field` scans those lines and returns the first match.
- **No new tests.** The ticket asks for the checker's tests to pass unchanged. They already pin every message and refusal path, and the differential run covers the byte-identical requirement beyond them.
