import re
import unittest
from pathlib import Path

TEMPLATES = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "agent_kit"
    / "payload"
    / "templates"
)

BEGIN = "<!-- agent-kit:begin -->"
END = "<!-- agent-kit:end -->"
PLACEHOLDER = "{{KIT_BLOCK}}"

TEMPLATE_NAMES = (
    "AGENTS.md",
    "GLOSSARY.md",
    "docs/agents/project.md",
)

# The project layout of design.md §4; a template may name only these paths.
DESIGN_PATHS = (
    ".agents/kit/**",
    ".agents/skills/**",
    ".agents/hooks.local/pre-commit",
    ".agents/kit.lock",
    ".gitattributes",
    "AGENTS.md",
    "GLOSSARY.md",
    "docs/agents/project.md",
    "docs/adr/",
    ".scratch/",
)

FORBIDDEN = ("rc-machines", "src/server", "front-loader", "servo")

INLINE_CODE = re.compile(r"`([^`\n]+)`")
PATH_LIKE = re.compile(r"^[\w./-]+$")


def is_design_path(path):
    for allowed in DESIGN_PATHS:
        if allowed.endswith("/**"):
            prefix = allowed[:-2]
            if path == prefix[:-1] or path.startswith(prefix):
                return True
        elif path == allowed:
            return True
    return False


class TemplateTests(unittest.TestCase):
    def read(self, name):
        path = TEMPLATES / name
        self.assertTrue(path.is_file(), f"missing template: {name}")
        return path.read_text(encoding="utf-8")

    def test_every_template_exists(self):
        for name in TEMPLATE_NAMES:
            with self.subTest(name=name):
                self.assertTrue((TEMPLATES / name).is_file(), name)

    def test_agents_template_has_one_marker_pair_around_the_placeholder(self):
        content = self.read("AGENTS.md")

        self.assertEqual(content.count(BEGIN), 1)
        self.assertEqual(content.count(END), 1)

        begin = content.index(BEGIN)
        end = content.index(END)
        self.assertLess(begin, end)
        self.assertEqual(content[begin + len(BEGIN) : end].strip(), PLACEHOLDER)

    def test_agents_template_uses_the_placeholder_once(self):
        self.assertEqual(self.read("AGENTS.md").count(PLACEHOLDER), 1)

    def test_no_other_template_uses_a_placeholder(self):
        for name in TEMPLATE_NAMES:
            if name == "AGENTS.md":
                continue
            with self.subTest(name=name):
                self.assertNotIn("{{", self.read(name))

    def test_templates_mention_no_rc_machines_specifics(self):
        for name in TEMPLATE_NAMES:
            content = self.read(name)
            for word in FORBIDDEN:
                with self.subTest(name=name, word=word):
                    self.assertNotIn(word, content)

    def test_every_path_a_template_names_is_in_the_design_layout(self):
        for name in TEMPLATE_NAMES:
            content = self.read(name)
            for candidate in INLINE_CODE.findall(content):
                if not PATH_LIKE.match(candidate):
                    continue
                if "/" not in candidate and not candidate.endswith(".md"):
                    continue
                with self.subTest(name=name, path=candidate):
                    self.assertTrue(
                        is_design_path(candidate),
                        f"{name} names {candidate}, which design.md §4 does not place",
                    )
