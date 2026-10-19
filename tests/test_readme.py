"""The README's install examples: copy-pasteable, with no developer's absolute path."""

import re
import unittest
from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"

PLACEHOLDER = "<path-to-this-repo>"

COMMANDS = (
    "pipx install --python 3.14",
    "uv tool install --python 3.14",
    "pipx install --force --python 3.14",
    "uv tool install --force --python 3.14",
)

WINDOWS_PATH = re.compile(r"[A-Za-z]:\\")


class ReadmeInstallTests(unittest.TestCase):
    def read(self):
        self.assertTrue(README.is_file(), "missing README.md")
        return README.read_text(encoding="utf-8")

    def test_each_install_and_upgrade_example_names_the_placeholder(self):
        content = self.read()
        for command in COMMANDS:
            with self.subTest(command=command):
                self.assertIn(f"{command} {PLACEHOLDER}", content)

    def test_the_examples_carry_no_absolute_path(self):
        content = self.read()
        self.assertIsNone(WINDOWS_PATH.search(content))
        self.assertNotIn("PycharmProjects", content)
