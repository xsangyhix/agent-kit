Labels: ready-for-human
Status: in-review

## Description

The kit's version lives in two files, `src/agent_kit/__init__.py` and
`pyproject.toml`, and a bump also has to touch `CHANGELOG.md`, the installed copy's
`.agents/kit.lock` and the tests. Today only `docs/agents/project.md` says "bump both
together"; there is no procedure, so a partial bump is easy and the sync check catches
it only at commit time. Nothing checks that the two version files agree.

Add one canonical bump procedure to `README.md` under "Maintaining the kit", point
`docs/agents/project.md` at it, and remove the failure modes the procedure would
otherwise have to describe:

- De-hardcode the version literals in `tests/test_cli.py` and `tests/test_init.py`,
  so they read `agent_kit.__version__`. `tests/test_changelog.py` keeps its literal,
  because pinning the changelog heading is its job.
- Add a test that reads `pyproject.toml` with `tomllib` and asserts its `version`
  equals `agent_kit.__version__`, so a one-sided bump fails the suite.

The instruction is harness-neutral: a bump does not change with the harness. Only the
`harness` field of `.agents/kit.lock` varies, and installer code records it; nobody
edits it by hand.

The procedure covers, in order:

1. Bump `src/agent_kit/__init__.py` and `pyproject.toml` together.
2. Add a `CHANGELOG.md` entry under the new `## [X.Y.Z] - YYYY-MM-DD` heading and
   update `VERSION_HEADING` in `tests/test_changelog.py` to match.
3. Run the suite.
4. Refresh the installed copy with the tool run from this repository root with `src`
   on `PYTHONPATH`, so `.agents/kit.lock` carries the new `kit_version`.
5. Run `py -3.14 tools/check_payload_sync.py`.
6. Commit. The user merges `agent/<feature-slug>` into `dev` and tags `vX.Y.Z` there.
7. Verify `agent-kit --version` reports the new version.

## Blocked by

None.

## Acceptance criteria

- [x] `README.md`'s "Maintaining the kit" section contains the ordered procedure listed in the Description, including the harness-neutral sentence and the `vX.Y.Z` tag step.
- [x] `docs/agents/project.md`'s Release section keeps its short rule and points at the README procedure instead of duplicating it.
- [x] `tests/test_cli.py` and `tests/test_init.py` contain no `0.1.0` literal; they use `agent_kit.__version__`.
- [x] A test asserts that `pyproject.toml`'s `version` equals `agent_kit.__version__`, and fails when either is changed alone.
- [x] `tests/test_changelog.py` still pins the changelog heading, and the procedure says to update it.
- [x] The whole suite passes and `py -3.14 tools/check_payload_sync.py` exits 0.

## Out of scope

- Bumping `0.1.0` itself or tagging the first release (agent-kit/28-tag-first-release).
- Automating the bump, or making `pyproject.toml` read the version dynamically.
- Adding a harness or changing the harness table.
- The SemVer policy: `CHANGELOG.md` already states it; the procedure only points at it.
