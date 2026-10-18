import unittest

from . import support

SHELL = support.find_shell()


@unittest.skipUnless(
    SHELL,
    "the pre-commit hook is a POSIX shell script and no sh or bash was found",
)
class PreCommitHookGateTests(unittest.TestCase):
    """Pin the `dev` gate exactly as ticket 04 verified it by hand."""

    def make_repo(self, branch):
        repo = support.GitRepo(branch)
        self.addCleanup(repo.close)
        repo.add_hook_fixtures()
        return repo

    def test_dev_refuses_agent_session_with_both_markers(self):
        repo = self.make_repo("dev")

        result = repo.run_hook(SHELL, markers=support.AI_MARKERS)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("dev commit mode: agent session", result.stdout)

    def test_dev_refuses_agent_session_with_ai_agent_only(self):
        repo = self.make_repo("dev")

        result = repo.run_hook(SHELL, markers=("AI_AGENT",))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("dev commit mode: agent session", result.stdout)

    def test_dev_refuses_agent_session_with_opencode_only(self):
        repo = self.make_repo("dev")

        result = repo.run_hook(SHELL, markers=("OPENCODE",))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("dev commit mode: agent session", result.stdout)

    def test_dev_allows_the_human_and_says_so(self):
        repo = self.make_repo("dev")

        result = repo.run_hook(SHELL)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("dev commit mode: human", result.stdout)

    def test_agent_branch_allows_agent_session(self):
        repo = self.make_repo("agent/test")

        result = repo.run_hook(SHELL, markers=support.AI_MARKERS)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_agent_branch_allows_the_human(self):
        repo = self.make_repo("agent/test")

        result = repo.run_hook(SHELL)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


@unittest.skipUnless(
    SHELL,
    "the pre-commit hook is a POSIX shell script and no sh or bash was found",
)
class LocalHookTests(unittest.TestCase):
    """The project-owned step runs after the kit's checks and sets the status."""

    def make_repo(self, branch):
        repo = support.GitRepo(branch)
        self.addCleanup(repo.close)
        repo.add_hook_fixtures()
        return repo

    def test_local_hook_runs_and_its_success_is_the_hook_success(self):
        repo = self.make_repo("agent/test")
        repo.write(
            ".agents/hooks.local/pre-commit",
            "#!/bin/sh\ntouch local-hook-ran\n",
        )

        result = repo.run_hook(SHELL)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((repo.root / "local-hook-ran").exists())

    def test_local_hook_failure_status_is_the_hook_status(self):
        repo = self.make_repo("agent/test")
        repo.write(".agents/hooks.local/pre-commit", "#!/bin/sh\nexit 3\n")

        result = repo.run_hook(SHELL)

        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)

    def test_local_hook_sees_the_python_interpreter_and_branch(self):
        repo = self.make_repo("dev")
        repo.write(
            ".agents/hooks.local/pre-commit",
            "#!/bin/sh\n"
            "printf '%s\\n' \"$PYTHON\" > local-hook-env\n"
            "printf '%s\\n' \"$branch\" >> local-hook-env\n",
        )

        result = repo.run_hook(SHELL)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        python, branch = (
            (repo.root / "local-hook-env").read_text(encoding="utf-8").splitlines()
        )
        self.assertTrue(python)
        self.assertEqual(branch, "dev")

    def test_no_local_hook_is_allowed(self):
        repo = self.make_repo("agent/test")

        result = repo.run_hook(SHELL)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


@unittest.skipUnless(
    SHELL,
    "the pre-commit hook is a POSIX shell script and no sh or bash was found",
)
class HarnessMarkerTests(unittest.TestCase):
    """The harness's marker names drive detection; the defaults are only a fallback."""

    def make_repo(self, branch):
        repo = support.GitRepo(branch)
        self.addCleanup(repo.close)
        repo.add_hook_fixtures()
        return repo

    def test_custom_marker_refuses_the_protected_branch(self):
        repo = self.make_repo("dev")
        repo.write(".agents/kit/harness.sh", 'AGENT_MARKERS="MY_AGENT"\n')

        result = repo.run_hook(
            SHELL, markers=("MY_AGENT",), clear_markers=("MY_AGENT",)
        )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("dev commit mode: agent session", result.stdout)

    def test_custom_marker_ignores_the_default_markers(self):
        repo = self.make_repo("dev")
        repo.write(".agents/kit/harness.sh", 'AGENT_MARKERS="MY_AGENT"\n')

        result = repo.run_hook(
            SHELL, markers=("OPENCODE",), clear_markers=("MY_AGENT",)
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("dev commit mode: human", result.stdout)

    def test_missing_harness_warns_and_refuses_the_default_marker(self):
        repo = self.make_repo("dev")
        (repo.root / ".agents/kit/harness.sh").unlink()

        result = repo.run_hook(SHELL, markers=("OPENCODE",))

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("harness.sh is missing", result.stdout)


class HookSourceTests(unittest.TestCase):
    """Facts about the hook that have no observable behaviour of their own."""

    def test_interpreter_is_resolved_once_and_uses_the_kit_checker(self):
        hook = support.HOOK.read_text(encoding="utf-8")

        self.assertEqual(hook.count('[ -f "./.venv/Scripts/python.exe" ]'), 1)
        self.assertEqual(hook.count('[ -f "./.venv/bin/python" ]'), 1)
        self.assertIn('"$PYTHON" .agents/kit/check_tracker.py', hook)

    def test_protected_branch_is_declared_on_exactly_one_line(self):
        hook = support.HOOK.read_text(encoding="utf-8")

        lines = [
            line for line in hook.splitlines() if "PROTECTED_BRANCH=dev" in line
        ]

        self.assertEqual(len(lines), 1)

    def test_hook_has_no_project_specific_references(self):
        hook = support.HOOK.read_text(encoding="utf-8")

        self.assertNotIn("src/server", hook)
        self.assertNotIn("build_release", hook)
        self.assertNotIn("scripts/", hook)


if __name__ == "__main__":
    unittest.main()
