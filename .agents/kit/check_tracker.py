"""Validate the issue tracker's file invariants.

Run by ``.agents/kit/hooks/pre-commit``. Only files staged under ``.scratch/``
are checked, so the cost is proportional to the change.

Rules enforced (``.agents/kit/adr/0004-workflow-state-machine.md``,
``.agents/kit/adr/0005-issue-labels.md``, ``.agents/kit/workflow.md``):

* every tracked unit is UTF-8 and carries a ``Status:`` line using one of the
  eight states;
* a ``Labels:`` line, if present, uses one of the five canonical labels;
* a file under ``issues/closed/`` is ``done`` and carries no label other
  than ``wontfix``;
* a file under ``issues/`` is not ``done`` (it has not been closed yet).

Feature-level documents that are not tracked units -- retros, research notes --
sit beside ``issues/`` and are skipped.
"""

import re
import subprocess
import sys
from pathlib import Path

TRACKER = ".scratch"
UNIT_MARKER = "/issues/"
CLOSED_MARKER = "/issues/closed/"

STATES = (
    "draft",
    "awaiting-agent",
    "questioning",
    "in-progress",
    "in-review",
    "review-feedback",
    "blocked",
    "done",
)

LABELS = (
    "needs-triage",
    "needs-info",
    "ready-for-agent",
    "ready-for-human",
    "wontfix",
)

HEADER_LINES = 12


def staged_tracker_files():
    """Yield repo-relative paths of staged markdown files under the tracker."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return
    for name in result.stdout.split("\0"):
        if name.startswith(TRACKER + "/") and name.endswith(".md"):
            yield name


def parse_header(text):
    """Return the ``Status:`` and ``Labels:`` values from a file's header."""
    status = None
    labels = None
    for line in text.splitlines()[:HEADER_LINES]:
        if status is None:
            match = re.match(r"^Status:\s*(.+?)\s*$", line)
            if match:
                status = match.group(1)
        if labels is None:
            match = re.match(r"^Labels:\s*(.+?)\s*$", line)
            if match:
                labels = match.group(1)
    return status, labels


def check(name, status, labels, problems):
    closed = CLOSED_MARKER in name

    if status is None:
        problems.append(f"{name}: no 'Status:' line in the header")
    elif status not in STATES:
        problems.append(
            f"{name}: unknown status '{status}' "
            f"(expected one of: {', '.join(STATES)})"
        )

    if labels is not None and labels not in LABELS:
        problems.append(
            f"{name}: unknown label '{labels}' "
            f"(expected one of: {', '.join(LABELS)})"
        )

    if closed:
        if status != "done":
            problems.append(
                f"{name}: lives in issues/closed/ but is '{status}' (expected 'done')"
            )
        if labels is not None and labels != "wontfix":
            problems.append(
                f"{name}: closed issues carry no label other than 'wontfix'; "
                f"remove the '{labels}' label"
            )
    elif status == "done":
        problems.append(
            f"{name}: is 'done' but still under issues/; move it to issues/closed/"
        )


def main():
    problems = []
    for name in staged_tracker_files():
        if not UNIT_MARKER in name:
            continue  # a feature-level doc, not a tracked unit
        path = Path(name)
        if not path.exists():
            continue  # deleted in this commit
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"{name}: cannot be read as UTF-8; save it as UTF-8")
            continue
        status, labels = parse_header(text)
        check(name, status, labels, problems)

    if problems:
        print("")
        print("Issue tracker check failed:")
        for problem in problems:
            print(f"  - {problem}")
        print("")
        print("See .agents/kit/workflow.md and .agents/kit/issue-tracker.md.")
        print("")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
