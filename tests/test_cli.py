import contextlib
import io
import tempfile
import unittest

from agent_kit import cli


class CliTests(unittest.TestCase):
    def run_main(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_version_prints_the_version_and_returns_zero(self):
        code, stdout, stderr = self.run_main(["--version"])

        self.assertEqual(code, 0)
        self.assertEqual(stdout, "agent-kit 0.1.0\n")
        self.assertEqual(stderr, "")

    def test_init_is_wired_to_the_installer(self):
        with tempfile.TemporaryDirectory() as folder:
            code, stdout, stderr = self.run_main(["init", folder])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("not the root of a git repository", stderr)

    def test_update_is_not_implemented(self):
        code, stdout, stderr = self.run_main(["update"])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("not implemented yet", stderr)

    def test_no_arguments_prints_help_and_returns_two(self):
        code, stdout, stderr = self.run_main([])

        self.assertEqual(code, 2)
        self.assertIn("usage:", stdout)
        self.assertIn("init", stdout)
        self.assertIn("update", stdout)
        self.assertEqual(stderr, "")
