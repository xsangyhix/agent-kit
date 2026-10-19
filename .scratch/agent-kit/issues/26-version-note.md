Labels: ready-for-human
Status: in-review

## Description

There is no changelog or version note. Before the first release, add a short `0.1.0` note that says what the kit ships, so a reader knows what the first published version contains.

## Blocked by

None.

## Acceptance criteria

- [x] `CHANGELOG.md` exists at the repo root with a `0.1.0` entry.
- [x] The entry covers: the `agent-kit init` / `agent-kit update` commands; the workflow docs, issue tracker and guardrails installed under `.agents/`; and the vendored skills snapshot.
- [x] It records the kit's own license as "see LICENSE" and the vendored skills as MIT.
- [x] Written in English, plain markdown, as a project document (not an issue file).

## Out of scope

- Bumping the version: it is already `0.1.0` in both `src/agent_kit/__init__.py` and `pyproject.toml`.
- Editing `README.md`'s install examples (agent-kit/27-readme-install-paths).
