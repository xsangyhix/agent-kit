Labels: ready-for-agent
Status: awaiting-agent

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

- [ ] The three items are done.
- [ ] `tests/guardrail/test_check_tracker.py` passes unchanged. If it reaches into a renamed parameter, adapt only that.
- [ ] `.agents/kit/check_tracker.py` is identical to the payload, and `.agents/kit.lock` matches (the `update` run exits 0).
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- New tracker rules, or support for more than one label.
- Taking the change into rc-machines (agent-kit/22-rc-machines-takes-the-kit-fixes).
