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

## Release

The version lives in `src/agent_kit/__init__.py` and `pyproject.toml`; bump both together; the user tags `vX.Y.Z` on `dev`. Skills are refreshed with `python tools/refresh_skills.py <sha>`, never edited by hand.

## ADR numbering

Project ADRs in `docs/adr/` start at `0001` unless stated otherwise here.

## Other rules

Python 3.14 compatibility and stdlib only (design §2; the design lives in the rc-machines repo at `.scratch/agent-kit/design.md`). The design of the kit is recorded in `README.md`.
