"""Tests for the payload sync check (tools/check_payload_sync.py)."""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

from agent_kit import __version__, installer
from tests.guardrail.support import (
    FakeStdin,
    GitRepo,
    REPO_ROOT,
    copied_payload,
    snapshot,
)

TOOL = REPO_ROOT / "tools" / "check_payload_sync.py"

SPEC = importlib.util.spec_from_file_location("check_payload_sync", TOOL)
check_payload_sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_payload_sync)

KIT_FILE = "kit/check_tracker.py"
SKILL_FILE = "skills/engineering/tdd/SKILL.md"


class PayloadSyncTests(unittest.TestCase):
    def setUp(self):
        self.repo = GitRepo()
        self.addCleanup(self.repo.close)
        self.root = self.repo.root
        self.payload = copied_payload(self)

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = installer.init(
                self.root,
                None,
                False,
                FakeStdin(),
                stdout,
                payload=self.payload,
            )
        self.assertEqual(code, 0, stdout.getvalue() + stderr.getvalue())

        self._saved_root = check_payload_sync.ROOT
        self._saved_payload = check_payload_sync.PAYLOAD_DIR
        check_payload_sync.ROOT = self.root
        check_payload_sync.PAYLOAD_DIR = self.payload
        self.addCleanup(self._restore_main_roots)

    def _restore_main_roots(self):
        check_payload_sync.ROOT = self._saved_root
        check_payload_sync.PAYLOAD_DIR = self._saved_payload

    def run_check(self):
        return check_payload_sync.check(self.root, self.payload)

    def run_main(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = check_payload_sync.main()
        return code, stdout.getvalue()

    def installed(self, relative):
        return self.root / relative

    def payload_file(self, relative):
        return self.payload / relative

    def edit(self, path, text="edited\n"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def assert_reports(self, problems, *expected):
        for line in expected:
            self.assertIn(line, problems)
        self.assertNotEqual(problems, [])

    # -- the clean install -------------------------------------------------

    def test_clean_install_is_in_sync(self):
        self.assertEqual(self.run_check(), [])

    def test_this_repository_is_in_sync(self):
        self.assertEqual(check_payload_sync.check(REPO_ROOT), [])

    # -- the installed copy ------------------------------------------------

    def test_installed_file_edited_is_modified(self):
        self.edit(self.installed(".agents/kit/check_tracker.py"))
        self.assert_reports(
            self.run_check(),
            ".agents/kit/check_tracker.py (modified)",
        )

    def test_installed_skill_edited_is_modified(self):
        self.edit(self.installed(".agents/skills/engineering/tdd/SKILL.md"))
        self.assert_reports(
            self.run_check(),
            ".agents/skills/engineering/tdd/SKILL.md (modified)",
        )

    def test_installed_file_deleted_is_missing(self):
        self.installed(".agents/kit/check_tracker.py").unlink()
        self.assert_reports(
            self.run_check(),
            ".agents/kit/check_tracker.py (missing)",
        )

    def test_installed_extra_file_is_not_in_the_payload(self):
        self.edit(self.installed(".agents/kit/stray.md"))
        self.assert_reports(
            self.run_check(),
            ".agents/kit/stray.md (not in the payload)",
        )

    def test_installed_extra_skill_is_not_in_the_payload(self):
        self.edit(self.installed(".agents/skills/engineering/stray/SKILL.md"))
        self.assert_reports(
            self.run_check(),
            ".agents/skills/engineering/stray/SKILL.md (not in the payload)",
        )

    # -- the payload -------------------------------------------------------

    def test_payload_file_edited_after_install_is_modified(self):
        self.edit(self.payload_file(KIT_FILE))
        self.assert_reports(
            self.run_check(),
            ".agents/kit/check_tracker.py (modified)",
        )

    def test_payload_skill_edited_after_install_is_modified(self):
        self.edit(self.payload_file(SKILL_FILE))
        self.assert_reports(
            self.run_check(),
            ".agents/skills/engineering/tdd/SKILL.md (modified)",
        )

    # -- generated output --------------------------------------------------

    def test_stale_harness_script_is_reported(self):
        self.edit(self.installed(".agents/kit/harness.sh"), "AGENT_MARKERS=''\n")
        self.assert_reports(
            self.run_check(),
            ".agents/kit/harness.sh (modified)",
        )

    def test_payload_block_edited_after_install_is_reported(self):
        self.edit(self.payload_file("agents-block.md"), "<!-- agent-kit:begin -->\nnew\n<!-- agent-kit:end -->\n")
        self.assert_reports(
            self.run_check(),
            "AGENTS.md (kit block does not match the payload)",
        )

    def test_stale_kit_version_is_reported(self):
        lock_path = self.installed(".agents/kit.lock")
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        data["kit_version"] = "0.0.0"
        lock_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.assert_reports(
            self.run_check(),
            f".agents/kit.lock (kit_version '0.0.0' does not match {__version__!r})",
        )

    def test_unknown_harness_is_reported_and_skips_harness_script(self):
        lock_path = self.installed(".agents/kit.lock")
        lock_path.write_text(
            lock_path.read_text(encoding="utf-8").replace(
                '"harness": "opencode"', '"harness": "unknown"'
            ),
            encoding="utf-8",
        )
        problems = self.run_check()
        self.assert_reports(
            problems,
            ".agents/kit.lock (unknown harness 'unknown')",
        )
        self.assertNotIn(
            ".agents/kit/harness.sh (modified)",
            problems,
        )

    # -- line endings and ignored files ------------------------------------

    def test_crlf_copies_of_both_sides_still_pass(self):
        for folder in (
            self.root / ".agents" / "kit",
            self.root / ".agents" / "skills",
            self.payload / "kit",
            self.payload / "skills",
        ):
            for path in folder.rglob("*"):
                if path.is_file():
                    self._write_crlf(path)
        self._write_crlf(self.root / "AGENTS.md")
        self.assertEqual(self.run_check(), [])

    def _write_crlf(self, path):
        data = path.read_bytes().replace(b"\r\n", b"\n")
        path.write_bytes(data.replace(b"\n", b"\r\n"))

    def test_bytecode_cache_files_are_ignored(self):
        cache = self.installed(".agents/kit/__pycache__/check_tracker.cpython-314.pyc")
        self.edit(cache)
        self.edit(self.installed(".agents/skills/engineering/tdd/stale.pyc"))
        self.edit(self.payload_file("kit/__pycache__/stale.pyc"))
        self.assertEqual(self.run_check(), [])

    # -- broken checkouts --------------------------------------------------

    def test_missing_kit_folder_is_one_line(self):
        shutil.rmtree(self.installed(".agents/kit"))
        self.assertEqual(self.run_check(), [".agents/kit (missing)"])

    def test_missing_skills_folder_is_one_line(self):
        shutil.rmtree(self.installed(".agents/skills"))
        self.assertEqual(self.run_check(), [".agents/skills (missing)"])

    def test_missing_payload_is_one_line(self):
        shutil.rmtree(self.payload)
        self.assertEqual(
            self.run_check(),
            [f"{self.payload.as_posix()} (missing)"],
        )

    def test_missing_payload_kit_folder_is_one_line(self):
        shutil.rmtree(self.payload / "kit")
        self.assertEqual(
            self.run_check(),
            [f"{(self.payload / 'kit').as_posix()} (missing)"],
        )

    def test_missing_lock_is_one_line(self):
        self.installed(".agents/kit.lock").unlink()
        self.assertEqual(self.run_check(), [".agents/kit.lock (missing)"])

    def test_corrupt_lock_is_one_line(self):
        self.edit(self.installed(".agents/kit.lock"), "{not json\n")
        problems = self.run_check()
        self.assertEqual(len(problems), 1)
        self.assertIn("not valid JSON", problems[0])

    def test_missing_agents_file_is_one_line(self):
        self.installed("AGENTS.md").unlink()
        self.assertEqual(self.run_check(), ["AGENTS.md (missing)"])

    def test_broken_agents_block_is_one_line(self):
        agents = self.installed("AGENTS.md")
        text = agents.read_text(encoding="utf-8")
        agents.write_text(
            text.replace("<!-- agent-kit:end -->", ""),
            encoding="utf-8",
        )
        problems = self.run_check()
        self.assertEqual(len(problems), 1)
        self.assertTrue(problems[0].startswith("AGENTS.md (broken kit block:"))

    # -- main and side effects ---------------------------------------------

    def test_main_prints_nothing_and_returns_zero_when_clean(self):
        code, output = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(output, "")

    def test_main_prints_the_problems_and_returns_one_when_drifted(self):
        self.edit(self.installed(".agents/kit/check_tracker.py"))
        code, output = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("  - .agents/kit/check_tracker.py (modified)", output)
        self.assertIn("agent-kit update", output)

    def test_a_drifted_run_writes_nothing(self):
        self.edit(self.installed(".agents/kit/check_tracker.py"))
        before = snapshot(self.root)
        code, _ = self.run_main()
        self.assertEqual(code, 1)
        self.assertEqual(snapshot(self.root), before)

    # -- the script without an installed package ---------------------------

    @unittest.skipUnless(shutil.which("py"), "needs the Windows py launcher")
    def test_script_runs_from_the_repo_root_without_an_installed_package(self):
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in ("PYTHONPATH", "PYTHONHOME")
        }
        result = subprocess.run(
            ["py", "-3.14", str(TOOL)],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
