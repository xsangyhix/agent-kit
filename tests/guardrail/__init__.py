"""Tests for the payload's tracker checker and pre-commit hook.

Most tests build a throwaway git repository, stage files in it, and run the
real script against it. The interpreter-resolution and protected-branch tests
read the hook instead, because neither has observable behaviour. The package is
collected by the discovery run in the agent-kit design, §2.
"""
