import contextlib
import importlib.util
import io
import tarfile
import tempfile
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "refresh_skills.py"
COMMITTED_UPSTREAM = REPO / "src" / "agent_kit" / "payload" / "skills" / "UPSTREAM"

SPEC = importlib.util.spec_from_file_location("refresh_skills", TOOL)
refresh_skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refresh_skills)

SHA = "49dd158d1076134a641b33efb035946536778336"
TOP = f"skills-{SHA}"


def archive_member(name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    return info, io.BytesIO(data)


class RefreshSkillsTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.archive = self.root / "skills.tar.gz"
        self.target = self.root / "payload" / "skills"

    def tearDown(self):
        self.tempdir.cleanup()

    def write_archive(self, members):
        with tarfile.open(self.archive, "w:gz") as tar:
            for name, data in members.items():
                info, stream = archive_member(name, data)
                tar.addfile(info, stream)

    def standard_members(self, *, license_bytes=b"MIT License\n"):
        return {
            f"{TOP}/LICENSE": license_bytes,
            f"{TOP}/README.md": b"upstream readme\n",
            f"{TOP}/skills/engineering/README.md": b"engineering\n",
            f"{TOP}/skills/engineering/tdd/SKILL.md": b"---\nname: tdd\n---\n",
            f"{TOP}/skills/engineering/setup-matt-pocock-skills/SKILL.md": b"setup\n",
            f"{TOP}/skills/productivity/grilling/SKILL.md": b"---\nname: grilling\n---\n",
            f"{TOP}/skills/misc/wizard/SKILL.md": b"---\nname: wizard\n---\n",
            f"{TOP}/skills/in-progress/loop-me/SKILL.md": b"---\nname: loop-me\n---\n",
            f"{TOP}/skills/deprecated/old/SKILL.md": b"---\nname: old\n---\n",
        }

    def run_tool(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = refresh_skills.main(argv, target=self.target)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_commit_that_is_not_a_full_sha_is_a_usage_error(self):
        code, stdout, stderr = self.run_tool(["--archive", str(self.archive), "abc123"])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("40", stderr)
        self.assertFalse(self.target.exists())

    def test_snapshot_copies_the_four_categories_license_and_record(self):
        members = self.standard_members()
        self.write_archive(members)
        self.target.mkdir(parents=True)
        (self.target / "stale.txt").write_text("old snapshot\n")

        code, stdout, stderr = self.run_tool(["--archive", str(self.archive), SHA])

        self.assertEqual(code, 0, stderr)
        self.assertEqual(stderr, "")
        self.assertIn("4 skills", stdout)
        self.assertFalse((self.target / "stale.txt").exists())

        for category in ("engineering", "productivity", "misc", "in-progress"):
            self.assertTrue((self.target / category).is_dir(), category)

        self.assertFalse((self.target / "deprecated").exists())
        self.assertFalse(
            (self.target / "engineering" / "setup-matt-pocock-skills").exists()
        )
        self.assertFalse((self.target / "README.md").exists())
        self.assertEqual(
            (self.target / "engineering" / "tdd" / "SKILL.md").read_bytes(),
            members[f"{TOP}/skills/engineering/tdd/SKILL.md"],
        )
        self.assertEqual(
            (self.target / "LICENSE").read_bytes(), members[f"{TOP}/LICENSE"]
        )
        self.assertEqual(
            (self.target / "UPSTREAM").read_text(encoding="utf-8"),
            "source: https://github.com/mattpocock/skills\n"
            f"commit: {SHA}\n"
            f"fetched: {date.today().isoformat()}\n"
            "license: MIT (see LICENSE in this folder)\n"
            "excluded: skills/deprecated/, skills/engineering/setup-matt-pocock-skills/\n",
        )

    def test_generated_record_matches_the_committed_upstream_file(self):
        self.write_archive(self.standard_members())

        code, stdout, stderr = self.run_tool(["--archive", str(self.archive), SHA])

        self.assertEqual(code, 0, stderr)
        generated = (self.target / "UPSTREAM").read_text(encoding="utf-8")
        committed = COMMITTED_UPSTREAM.read_text(encoding="utf-8")
        expected = "".join(
            f"fetched: {date.today().isoformat()}\n"
            if line.startswith("fetched: ")
            else line
            for line in committed.splitlines(keepends=True)
        )
        self.assertEqual(generated, expected)

    def test_excluded_tuple_drives_both_the_copy_and_the_record(self):
        self.write_archive(self.standard_members())
        original = refresh_skills.EXCLUDED
        refresh_skills.EXCLUDED = original + (
            "skills/misc",
            "skills/productivity/grilling",
        )
        self.addCleanup(setattr, refresh_skills, "EXCLUDED", original)

        code, stdout, stderr = self.run_tool(["--archive", str(self.archive), SHA])

        self.assertEqual(code, 0, stderr)
        self.assertFalse((self.target / "misc").exists())
        self.assertFalse((self.target / "productivity" / "grilling").exists())
        record = (self.target / "UPSTREAM").read_text(encoding="utf-8")
        self.assertIn(
            "excluded: skills/deprecated/, "
            "skills/engineering/setup-matt-pocock-skills/, "
            "skills/misc/, skills/productivity/grilling/\n",
            record,
        )

    def prepare_existing_payload(self):
        self.target.mkdir(parents=True)
        (self.target / "sentinel.txt").write_text("keep me\n")

    def assert_archive_refused(self, word):
        code, stdout, stderr = self.run_tool(["--archive", str(self.archive), SHA])

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn(word, stderr)
        self.assertEqual(
            {path.name for path in self.target.iterdir()}, {"sentinel.txt"}
        )

    def test_archive_without_license_is_refused(self):
        members = self.standard_members()
        del members[f"{TOP}/LICENSE"]
        self.write_archive(members)
        self.prepare_existing_payload()

        self.assert_archive_refused("LICENSE")

    def test_archive_without_a_category_is_refused(self):
        members = {
            name: data
            for name, data in self.standard_members().items()
            if not name.startswith(f"{TOP}/skills/in-progress/")
        }
        self.write_archive(members)
        self.prepare_existing_payload()

        self.assert_archive_refused("in-progress")

    def test_member_with_parent_traversal_is_refused(self):
        members = self.standard_members()
        members[f"{TOP}/../evil.txt"] = b"escaped\n"
        self.write_archive(members)
        self.prepare_existing_payload()

        self.assert_archive_refused("..")

    def test_absolute_member_is_refused(self):
        members = self.standard_members()
        members["/evil.txt"] = b"escaped\n"
        self.write_archive(members)
        self.prepare_existing_payload()

        self.assert_archive_refused("unsafe path")

    def test_members_from_two_top_folders_are_refused(self):
        members = self.standard_members()
        members["other/evil.txt"] = b"escaped\n"
        self.write_archive(members)
        self.prepare_existing_payload()

        self.assert_archive_refused("top-level folder")
