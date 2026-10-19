# Project rules

This file holds the rules specific to this project. Agents read it before their first edit, as required by rule 7 of `.agents/kit/workflow.md`.

## Tests

Run the whole suite from the repository root:

```
py -3.14 -m unittest discover -s tests -t . -v
```

Set `SKIP_PACKAGING_TEST=1` to skip the wheel build in `tests/test_packaging.py`.

## Do not edit

`.agents/kit/` and `.agents/skills/` are this repo's **installed copy** of the kit. The source is `src/agent_kit/payload/`. Change the payload, then run `python -m agent_kit update` (with `PYTHONPATH=src`) to refresh the installed copy, and commit both.

The sync check enforces that: `py -3.14 tools/check_payload_sync.py` compares the installed copy, the lock and the kit block with the payload, and `.agents/hooks.local/pre-commit` runs it on every commit. A green suite and a passing commit therefore both include it.

## Release

The bump procedure is in `README.md` under "Maintaining the kit"; it names the files to change, the changelog entry, the installed-copy refresh and the sync check. The user tags `vX.Y.Z` on `dev`. Skills are refreshed with `python tools/refresh_skills.py <sha>`, never edited by hand.

## ADR numbering

Project ADRs in `docs/adr/` start at `0001` unless stated otherwise here.

## Other rules

Python 3.14 compatibility and stdlib only (design §2; the design lives in the rc-machines repo at `.scratch/agent-kit/design.md`). The design of the kit is recorded in `README.md`.
