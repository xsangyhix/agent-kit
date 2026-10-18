Labels: ready-for-agent
Status: awaiting-agent

## Description

From the Standards axis of the 2026-10-18 code review of the agent-kit effort (Duplicated Code). In `tools/refresh_skills.py`, the `UPSTREAM` template hard-codes the line `excluded: skills/deprecated/, skills/engineering/setup-matt-pocock-skills/`. The script's own constants already say the same thing: `CATEGORIES` decides which category folders are copied, so it implicitly drops `skills/deprecated/`, and `EXCLUDED` names the excluded skill folder. If someone changes the constants, the `UPSTREAM` record silently goes wrong.

Build the `excluded:` line from one source of truth. One option is a single tuple of excluded paths that both the copy logic and the `UPSTREAM` text use. Keep the line's format and order exactly as design §10 specifies: `skills/deprecated/` first, each path with a trailing `/`, joined by `, `.

The output for today's constants must be byte-identical to `src/agent_kit/payload/skills/UPSTREAM`, apart from the `fetched:` date. Do not re-run the refresh against upstream as part of this ticket.

Test-Driven Development: first pin today's `UPSTREAM` text in `tests/test_refresh_skills.py`, if it is not already pinned. Then add a test proving that a changed exclusion list is reflected in the `excluded:` line.

## Blocked by

None.

## Acceptance criteria

- [ ] The excluded paths are written down once in `tools/refresh_skills.py`.
- [ ] The generated `UPSTREAM` for the current constants matches the committed file byte for byte, except the date. A test asserts it.
- [ ] A test shows that a different exclusion list changes both what is copied and the `excluded:` line.
- [ ] `src/agent_kit/payload/skills/` is unchanged.
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Refreshing the snapshot to a newer upstream commit.
- Any other change to the refresh tool.
