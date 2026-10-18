Labels: ready-for-human
Status: in-review

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

- [x] Each of the six smells is fixed, or left with a reason recorded in the review.
- [x] No test that asserts output, exit codes or file contents changed. Tests that only reached into a removed private name or string state may be adapted.
- [x] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.
- [x] `PYTHONPATH=src py -3.14 -m agent_kit update` in this repo still reports no local changes and exits 0.

## Out of scope

- Any change in behaviour or wording.
- Adding type hints across the package. `cli.py` is the only module with them; whether to add them everywhere or remove them is a separate decision.
- `src/agent_kit/lock.py` beyond being the single owner of the lock path.

## Review

Implementation complete, submitted for review.

### Summary of changes

All six smells are fixed.

`src/agent_kit/installer.py`:

- **Kit-owned folders:** `_kit_folders(root, harness)` names the two folders, and `_kit_owned_paths(root, harness)` walks them once through `_files_under`. The init conflict scan, both deletion loops, `_local_changes` and `_kit_owned_hashes` use them; `_kit_owned_files` is gone.
- **Opening checks:** `_resolve_inputs`, `_require_git_root`, `_select_harness` and `_refuse_broken_block` hold what `init` and `update` shared. Messages, exit codes and streams are unchanged: exit-2 usage errors still go to `sys.stderr`, exit-1 refusals to the injected `stdout`, in the same order in each command.
- **Block state:** `BlockKind` is an `enum.Enum` with `ABSENT`, `BAD` and `OK`. `find_block` returns the member and every caller compares identity instead of a string.
- **Constants:** `LOCK_FILE` is gone; the installer imports `lock.LOCK_NAME`. `HOOKS_DIR` is derived from `KIT_DIR`, and `HOOK`, `GITATTRIBUTES_LINE` and `_set_hooks_path` derive from `HOOKS_DIR`.
- **Summaries:** `_print_report(stdout, headline, sections, block_action)` prints both summaries' titled indented lists, the blank line after each and the shared two-line footer. `_print_summary` and `_print_update_summary` are gone; `update` builds its Updated/Added/Removed sections and passes them in.

`src/agent_kit/cli.py`:

- The unreachable "not implemented yet" branch at the end of `main` is removed.

`tests/test_init.py`:

- The block-state assertions now use `installer.BlockKind` with `assertIs`; no test that asserts output, exit codes or file contents changed.

### Verification

TDD: the `BlockTests` assertions were changed to the enum first and failed against the old string state (`AttributeError: module 'agent_kit.installer' has no attribute 'BlockKind'`). They passed once the enum landed. The other five smells are behaviour-preserving, so the existing suite is the proof; every test written for the previous tickets still passes unchanged.

```
py -3.14 -m unittest discover -s tests -t . -v
Ran 137 tests in 105.732s

OK (skipped=1)
```

The skip is the pre-existing Windows case, `test_the_installed_hook_keeps_its_mode_on_disk`; the packaging test ran and passed.

`PYTHONPATH=src py -3.14 -m agent_kit update` exits 0, prints no local-change lists, and changes no file on disk.

### Judgement calls

- **None of the six smells was left in place.** Each had a concrete shared helper or single owner, so leaving one would have kept a duplicate the next ticket would have to reconcile.
- **`BlockKind` rather than an enum named `BlockState`.** The existing `BlockState` is the namedtuple; keeping that name and adding `BlockKind` as its `state` field type avoids renaming the record and keeps the change inside the field the ticket called out.
- **`_kit_owned_paths` returns strings, not `Path`s.** `_files_under` already produced repo-relative POSIX strings, and the three callers work in those strings (printing, lock keys and `file_hash`). Returning `Path`s would force a conversion at every call site.
