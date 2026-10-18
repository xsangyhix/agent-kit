#!/usr/bin/env python3
"""Refresh the vendored Matt Pocock skill snapshot.

Usage:
    python tools/refresh_skills.py <commit-sha> [--archive PATH]

Without --archive the upstream tarball for the commit is downloaded. The
snapshot is written only after every validation passes.
"""

import argparse
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")

ARCHIVE_URL = "https://codeload.github.com/mattpocock/skills/tar.gz/{sha}"

CATEGORIES = ("engineering", "productivity", "misc", "in-progress")

EXCLUDED = ("skills/engineering/setup-matt-pocock-skills",)

UPSTREAM = (
    "source: https://github.com/mattpocock/skills\n"
    "commit: {sha}\n"
    "fetched: {fetched}\n"
    "license: MIT (see LICENSE in this folder)\n"
    "excluded: skills/deprecated/, skills/engineering/setup-matt-pocock-skills/\n"
)

DEFAULT_TARGET = (
    Path(__file__).resolve().parents[1] / "src" / "agent_kit" / "payload" / "skills"
)


class RefreshError(Exception):
    """A validation refused the refresh; nothing was written."""


def main(argv=None, *, target=None):
    parser = argparse.ArgumentParser(
        prog="refresh_skills.py",
        description="Refresh the vendored mattpocock/skills snapshot.",
    )
    parser.add_argument("sha", help="full 40-character commit SHA to vendor")
    parser.add_argument(
        "--archive",
        type=Path,
        help="read this .tar.gz instead of downloading the upstream archive",
    )
    args = parser.parse_args(argv)

    if not SHA_PATTERN.match(args.sha):
        print(
            f"error: commit must be 40 hex characters, got {args.sha!r}",
            file=sys.stderr,
        )
        return 2

    target = Path(target) if target is not None else DEFAULT_TARGET

    try:
        count = refresh(args.sha, target, args.archive)
    except RefreshError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Copied {count} skills to {target}.")
    return 0


def refresh(sha, target, archive=None):
    """Write a validated snapshot to target and return the number of skills."""
    target.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=".refresh-skills-", dir=target.parent))
    try:
        source_archive = archive
        if source_archive is None:
            source_archive = work / "upstream.tar.gz"
            download(sha, source_archive)

        extracted = work / "extracted"
        extracted.mkdir()
        top = extract(sha, source_archive, extracted)

        staging = work / "skills"
        build(sha, extracted, top, staging)

        remove_target(target)
        staging.replace(target)
        return count_skills(target)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def download(sha, destination):
    url = ARCHIVE_URL.format(sha=sha)
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            with destination.open("wb") as sink:
                shutil.copyfileobj(response, sink)
    except OSError as exc:
        raise RefreshError(f"could not download {url}: {exc}") from exc


def extract(sha, archive, destination):
    """Extract a validated archive and return its single top-level folder name."""
    try:
        with tarfile.open(archive, "r:gz") as tar:
            members = tar.getmembers()
            top = validate_members(members)
            tar.extractall(destination, filter="data")
    except (tarfile.TarError, OSError) as exc:
        raise RefreshError(f"could not read archive {archive}: {exc}") from exc

    top_dir = destination / top
    if not (top_dir / "LICENSE").is_file():
        raise RefreshError("archive has no LICENSE at its top level")
    for category in CATEGORIES:
        if not (top_dir / "skills" / category).is_dir():
            raise RefreshError(f"archive has no skills/{category}/ folder")
    return top


def validate_members(members):
    names = [member.name for member in members if member.name]
    if not names:
        raise RefreshError("archive is empty")

    for name in names:
        if is_unsafe(name):
            raise RefreshError(f"archive member has an unsafe path: {name!r}")

    tops = {name.split("/")[0] for name in names}
    if len(tops) != 1:
        listed = ", ".join(sorted(tops))
        raise RefreshError(f"archive members do not share one top-level folder: {listed}")
    return tops.pop()


def is_unsafe(name):
    if name.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", name):
        return True
    return ".." in name.replace("\\", "/").split("/")


def build(sha, extracted, top, staging):
    source = extracted / top
    staging.mkdir()

    def ignore(directory, names):
        base = Path(directory)
        ignored = []
        for name in names:
            relative = (base / name).relative_to(source).as_posix()
            if relative in EXCLUDED:
                ignored.append(name)
        return ignored

    for category in CATEGORIES:
        shutil.copytree(
            source / "skills" / category,
            staging / category,
            ignore=ignore,
        )

    shutil.copyfile(source / "LICENSE", staging / "LICENSE")
    record = UPSTREAM.format(sha=sha, fetched=date.today().isoformat())
    (staging / "UPSTREAM").write_bytes(record.encode("utf-8"))

    loose_markdown = [
        entry.name
        for entry in staging.iterdir()
        if entry.is_file() and entry.name.endswith(".md")
    ]
    if loose_markdown:
        listed = ", ".join(sorted(loose_markdown))
        raise RefreshError(f"snapshot would have markdown at its root: {listed}")


def remove_target(target):
    if target.is_dir() and not target.is_symlink():
        shutil.rmtree(target)
    elif target.exists() or target.is_symlink():
        target.unlink()


def count_skills(root):
    return sum(1 for path in root.rglob("SKILL.md") if path.is_file())


if __name__ == "__main__":
    sys.exit(main())
