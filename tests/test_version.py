"""The version is one value, duplicated only where the build needs it."""

import tomllib
import unittest
from pathlib import Path

from agent_kit import __version__

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"


class VersionTests(unittest.TestCase):
    def test_pyproject_declares_the_package_version(self):
        with PYPROJECT.open("rb") as file:
            data = tomllib.load(file)

        self.assertEqual(data["project"]["version"], __version__)
