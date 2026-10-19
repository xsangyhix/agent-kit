"""The release note: a 0.1.0 changelog entry that says what the kit ships."""

import unittest
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[1] / "CHANGELOG.md"

VERSION_HEADING = "## [0.1.0] - 2026-10-19"

SHIPPED = (
    "agent-kit init",
    "agent-kit update",
    "workflow",
    "issue tracker",
    "guardrails",
)


class ChangelogTests(unittest.TestCase):
    def read(self):
        self.assertTrue(CHANGELOG.is_file(), "missing CHANGELOG.md")
        return CHANGELOG.read_text(encoding="utf-8")

    def test_changelog_is_a_keep_a_changelog_document(self):
        self.assertEqual(self.read().splitlines()[0], "# Changelog")

    def test_changelog_has_a_dated_0_1_0_entry(self):
        self.assertEqual(self.read().count(VERSION_HEADING), 1)

    def test_entry_covers_what_the_kit_ships(self):
        content = self.read()
        for phrase in SHIPPED:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, content.lower())

    def test_entry_covers_the_skills_snapshot(self):
        self.assertIn("skills snapshot", self.read().lower())

    def test_entry_records_both_licenses(self):
        content = self.read()
        self.assertIn("see LICENSE", content)
        self.assertIn("MIT", content)
