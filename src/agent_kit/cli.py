"""Command-line interface for the agent kit."""

import argparse
import sys

from . import __version__

PROG = "agent-kit"


def _add_common_arguments(
    parser: argparse.ArgumentParser, force_help: str
) -> None:
    parser.add_argument("--force", action="store_true", help=force_help)
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="the project root (default: the current folder)",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Install and update the agent kit in a project.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    init = subparsers.add_parser(
        "init",
        help="install the agent kit into a project",
        description="Install the agent kit into a project.",
    )
    init.add_argument(
        "--harness",
        metavar="NAME",
        help="the harness to install for (opencode is the only value today)",
    )
    _add_common_arguments(
        init, "replace conflicting kit-owned paths after confirmation"
    )

    update = subparsers.add_parser(
        "update",
        help="update an installed agent kit",
        description="Update the agent kit in a project.",
    )
    _add_common_arguments(
        update, "discard changed kit-owned files after confirmation"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        return 0 if code is None else code

    if args.command is None:
        parser.print_help()
        return 2

    print(f"{PROG}: {args.command} is not implemented yet", file=sys.stderr)
    return 2
