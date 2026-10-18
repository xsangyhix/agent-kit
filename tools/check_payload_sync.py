#!/usr/bin/env python3
"""Check that the installed copy is what the current payload produces.

This is the repo-local sync check; it is not installed into projects. Run it
from the repository root:

    py -3.14 tools/check_payload_sync.py

It exits 0 and prints nothing when the installed copy, the lock and the kit
block all match the payload. Drift is reported one line per problem.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from agent_kit import __version__, installer  # noqa: E402
from agent_kit.harness import DEFAULT_HARNESS, HARNESSES  # noqa: E402
from agent_kit.lock import LOCK_NAME, file_hash, read_lock, text_hash  # noqa: E402

# main() binds these to the repository layout; tests point them elsewhere.
ROOT = REPO_ROOT
PAYLOAD_DIR = ROOT / "src" / "agent_kit" / "payload"

HEADER = "The installed copy is out of sync with the payload:"
HINT = (
    "Run `agent-kit update` (with PYTHONPATH=src) and commit the payload "
    "and the refreshed copy together."
)


def check(root, payload=None):
    """Return one line per problem; an empty list means the copy is in sync."""
    root = Path(root)
    payload = (
        Path(payload)
        if payload is not None
        else root / "src" / "agent_kit" / "payload"
    )
    problems = []

    if not payload.is_dir():
        return [f"{_display(root, payload)} (missing)"]

    lock, lock_problem = _read_lock(root)
    if lock_problem is not None:
        problems.append(lock_problem)

    harness = None
    if lock is not None:
        name = lock.get("harness")
        harness = HARNESSES.get(name)
        if harness is None:
            problems.append(f"{LOCK_NAME} (unknown harness {name!r})")

    skills_name = (
        harness.skills_dir
        if harness is not None
        else HARNESSES[DEFAULT_HARNESS].skills_dir
    )
    kit_dir = root / installer.KIT_DIR
    skills_dir = root / skills_name
    kit_ok = kit_dir.is_dir()
    skills_ok = skills_dir.is_dir()
    if not kit_ok:
        problems.append(f"{installer.KIT_DIR} (missing)")
    if not skills_ok:
        problems.append(f"{skills_name} (missing)")

    payload_kit = payload / "kit"
    payload_skills = payload / "skills"
    kit_source_ok = payload_kit.is_dir()
    skills_source_ok = payload_skills.is_dir()
    if not kit_source_ok:
        problems.append(f"{_display(root, payload_kit)} (missing)")
    if not skills_source_ok:
        problems.append(f"{_display(root, payload_skills)} (missing)")

    if kit_ok and kit_source_ok:
        problems.extend(
            _compare_tree(
                kit_dir,
                payload_kit,
                installer.KIT_DIR,
                allowed_extra=("harness.sh",),
            )
        )
    if skills_ok and skills_source_ok:
        problems.extend(
            _compare_tree(skills_dir, payload_skills, skills_name)
        )

    if harness is not None and kit_ok:
        problem = _harness_script_problem(kit_dir, harness)
        if problem is not None:
            problems.append(problem)

    if lock is not None:
        problems.extend(_lock_problems(root, lock, kit_ok, skills_ok, skills_name))

    problems.extend(_block_problems(root, payload, lock))

    return problems


def _read_lock(root):
    """Return (lock, problem); exactly one of them is None."""
    try:
        lock = read_lock(root)
    except ValueError as error:
        return None, str(error)
    if lock is None:
        return None, f"{LOCK_NAME} (missing)"
    return lock, None


def _display(root, path):
    """Return path relative to root when possible, as POSIX text."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _files_under(folder):
    """Return the POSIX paths under folder, ignoring bytecode caches."""
    return sorted(
        path.relative_to(folder).as_posix()
        for path in folder.rglob("*")
        if path.is_file() and not _ignored(path)
    )


def _ignored(path):
    return path.suffix == ".pyc" or "__pycache__" in path.parts


def _compare_tree(target_folder, source_folder, target_name, allowed_extra=()):
    """Return the differences between an installed tree and the payload."""
    problems = []
    source_files = set(_files_under(source_folder))
    target_files = set(_files_under(target_folder))

    for name in sorted(source_files):
        installed = target_folder / name
        if not installed.is_file():
            problems.append(f"{target_name}/{name} (missing)")
        elif file_hash(installed) != file_hash(source_folder / name):
            problems.append(f"{target_name}/{name} (modified)")

    for name in sorted(target_files - source_files - set(allowed_extra)):
        problems.append(f"{target_name}/{name} (not in the payload)")

    return problems


def _harness_script_problem(kit_dir, harness):
    """Return a problem line for harness.sh, or None when it is current."""
    path = kit_dir / "harness.sh"
    expected = installer.HARNESS_SH.format(
        markers=" ".join(harness.agent_markers)
    )
    if not path.is_file():
        return f"{installer.KIT_DIR}/harness.sh (missing)"
    if file_hash(path) != text_hash(expected):
        return f"{installer.KIT_DIR}/harness.sh (modified)"
    return None


def _lock_problems(root, lock, kit_ok, skills_ok, skills_name):
    """Return the lock's version, harness and file-list problems."""
    problems = []

    if lock.get("kit_version") != __version__:
        problems.append(
            f"{LOCK_NAME} (kit_version {lock.get('kit_version')!r} does not "
            f"match {__version__!r})"
        )

    # A missing kit or skills folder is already reported once. Without both
    # trees there is nothing to compare the lock's file list against.
    if not (kit_ok and skills_ok):
        return problems

    files = lock.get("files")
    if not isinstance(files, dict):
        problems.append(f"{LOCK_NAME} (files is not an object)")
        return problems

    installed = [
        f"{installer.KIT_DIR}/{name}"
        for name in _files_under(root / installer.KIT_DIR)
    ]
    installed += [
        f"{skills_name}/{name}"
        for name in _files_under(root / skills_name)
    ]

    if set(files) != set(installed):
        problems.append(f"{LOCK_NAME} (file list does not match the installed copy)")
        return problems

    for name in sorted(installed):
        if file_hash(root / name) != files[name]:
            problems.append(f"{LOCK_NAME} ({name} hash does not match)")

    return problems


def _block_problems(root, payload, lock):
    """Return problems with the kit block in AGENTS.md and its lock hash."""
    block_source = payload / "agents-block.md"
    if not block_source.is_file():
        return [f"{_display(root, block_source)} (missing)"]

    expected = installer.canonical_block_text(
        block_source.read_bytes().decode("utf-8")
    )
    problems = []
    agents_path = root / installer.AGENTS

    if not agents_path.is_file():
        problems.append(f"{installer.AGENTS} (missing)")
    else:
        text = agents_path.read_bytes().decode("utf-8")
        state = installer.classify_block(text)
        if state.state is installer.BlockKind.BAD:
            problems.append(
                f"{installer.AGENTS} (broken kit block: {state.reason})"
            )
        elif state.state is installer.BlockKind.ABSENT:
            problems.append(f"{installer.AGENTS} (kit block missing)")
        elif installer._block_text_for_hash(text, state) != expected:
            problems.append(
                f"{installer.AGENTS} (kit block does not match the payload)"
            )

    if lock is not None and text_hash(expected) != lock.get("agents_block"):
        problems.append(
            f"{LOCK_NAME} (agents_block hash does not match the payload)"
        )

    return problems


def main():
    """Check this repository; return 0 when in sync and 1 on drift."""
    problems = check(ROOT, PAYLOAD_DIR)
    if not problems:
        return 0

    print(HEADER)
    for problem in problems:
        print(f"  - {problem}")
    print(HINT)
    return 1


if __name__ == "__main__":
    sys.exit(main())
