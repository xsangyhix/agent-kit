"""The README's install examples and the maintenance procedure."""

import re
import unittest
from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"
PROJECT_RULES = (
    Path(__file__).resolve().parents[1] / "docs" / "agents" / "project.md"
)

PLACEHOLDER = "<path-to-this-repo>"

COMMANDS = (
    "pipx install --python 3.14",
    "uv tool install --python 3.14",
    "pipx install --force --python 3.14",
    "uv tool install --force --python 3.14",
)

WINDOWS_PATH = re.compile(r"[A-Za-z]:\\")

BUMP_STEPS = (
    "### Bumping the version",
    "`src/agent_kit/__init__.py`",
    "`pyproject.toml`",
    "`CHANGELOG.md`",
    "`tests/test_changelog.py`",
    "`PYTHONPATH=src`",
    "`py -3.14 tools/check_payload_sync.py`",
    "`vX.Y.Z`",
    "harness-neutral",
)


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


class ReadmeVersionBumpTests(unittest.TestCase):
    def test_the_maintenance_section_documents_the_bump(self):
        content = README.read_text(encoding="utf-8")

        for phrase in BUMP_STEPS:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, content)

    def test_the_project_rules_point_at_the_readme_procedure(self):
        content = PROJECT_RULES.read_text(encoding="utf-8")
        release = content.split("## Release", 1)[1].split("\n## ", 1)[0]

        self.assertIn("README.md", release)
        self.assertIn("Maintaining the kit", release)
