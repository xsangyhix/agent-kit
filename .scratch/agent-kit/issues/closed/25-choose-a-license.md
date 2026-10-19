Status: done

## Description

The kit's own files are unlicensed: `README.md` says "The kit's own files have no license yet", and `pyproject.toml` declares no `license`. The vendored skills snapshot is already MIT (unchanged, under Matt Pocock's license), so this ticket is only about the kit's own files: `src/agent_kit/*.py`, the payload's kit files and hook, `tools/`, and the docs.

The license choice itself is the user's decision; the agent cannot pick legal terms. Everything after the choice is mechanical: add a `LICENSE` file, declare the license and classifier in `pyproject.toml`, and update the README's "Credits and licenses" section.

## Blocked by

None.

## Acceptance criteria

- [x] A license is chosen and recorded (the user names it; MIT and Apache-2.0 are the common options for this kind of tool).
- [x] `LICENSE` (or `LICENSE.md`) exists at the repo root with the chosen license text.
- [x] `pyproject.toml` declares the license (a `license` field plus the matching `classifiers` entry).
- [x] `README.md`'s "Credits and licenses" section replaces "The kit's own files have no license yet." with the chosen license.
- [x] The whole suite still passes: `py -3.14 -m unittest discover -s tests -t .`.
- [x] `py -3.14 tools/check_payload_sync.py` still exits 0 (the payload and the installed copy are untouched by this change).

## Questions

1. Which license should the kit's own files carry? (MIT, Apache-2.0, or another)
   - Answer: MIT, `Copyright (c) 2026 Marcin Słoń`.

## Out of scope

- Re-licensing the vendored skills: they stay MIT under their upstream license.
- Any change to the payload, the installed copy, or code behaviour.
