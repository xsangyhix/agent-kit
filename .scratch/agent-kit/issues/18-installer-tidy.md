Labels: ready-for-agent
Status: awaiting-agent

## Description

A behaviour-preserving cleanup of `src/agent_kit/installer.py` and `src/agent_kit/cli.py`, from the Standards axis of the 2026-10-18 code review of the agent-kit effort. It runs after the installer bug fixes, so that the fixes land first and the shared code takes in the corrected behaviour.

Smells to remove. Line numbers are from the review and will have moved; find each by its description.

1. **The two kit-owned folders are rebuilt in many places.** The pair `(root / KIT_DIR, root / harness.skills_dir)` appears in init's conflict scan, init's `--force` deletion, update's deletion, `_local_changes` and `_kit_owned_files`. `_files_under` and `_kit_owned_files` also walk the same folders the same way. Replace these with one helper that names the kit-owned folders, and one walk.
2. **`init` and `update` duplicate their opening checks:** payload resolution, the git-root check, the unknown-harness message and the broken-block refusal. Share them. The messages, exit codes and streams must stay exactly as they are. Exit-2 usage errors go to `sys.stderr` and exit-1 refusals to the injected `stdout`: that split is deliberate, so keep it.
3. **The block state is a plain string.** `BlockState.state` holds `"absent"`, `"bad"` or `"ok"` and is tested by if-chains in several places. Make it an `enum.Enum`, or a small set of properties, and update the callers.
4. **Duplicated constants.** `installer.LOCK_FILE` repeats `lock.LOCK_NAME`: keep one. `_set_hooks_path` hard-codes `".agents/kit/hooks"`: derive it from `KIT_DIR`, and derive `GITATTRIBUTES_LINE` from it too if that reads well.
5. **Duplicated summary code.** `_print_summary` and `_print_update_summary` each print titled, indented lists and the same two-line footer. Extract one helper for both.
6. **Dead branch in `cli.py`.** The final `"… is not implemented yet"` branch of `main` cannot be reached: argparse accepts only `init` and `update`. Remove it.

Output must stay byte-identical for every command and outcome. The existing tests are the proof. If a smell turns out not to be worth fixing once you are in the code, leave it, and say why in the review.

## Blocked by

- agent-kit/14-init-force-checks-before-deleting
- agent-kit/15-agents-md-line-endings
- agent-kit/16-force-confirmation-lists-deletions-only
- agent-kit/17-markers-on-their-own-line

## Acceptance criteria

- [ ] Each of the six smells is fixed, or left with a reason recorded in the review.
- [ ] No test that asserts output, exit codes or file contents changed. Tests that only reached into a removed private name or string state may be adapted.
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.
- [ ] `PYTHONPATH=src py -3.14 -m agent_kit update` in this repo still reports no local changes and exits 0.

## Out of scope

- Any change in behaviour or wording.
- Adding type hints across the package. `cli.py` is the only module with them; whether to add them everywhere or remove them is a separate decision.
- `src/agent_kit/lock.py` beyond being the single owner of the lock path.
