import unittest

from . import support


class CheckTrackerTests(unittest.TestCase):
    def setUp(self):
        self.repo = support.GitRepo()
        self.addCleanup(self.repo.close)

    def assert_refused(self, result, *fragments):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for fragment in fragments:
            self.assertIn(fragment, result.stdout)

    def test_valid_active_ticket_passes(self):
        self.repo.write(
            ".scratch/effort/issues/01-a.md",
            "Labels: ready-for-agent\nStatus: awaiting-agent\n",
        )
        self.repo.stage(".scratch")

        result = self.repo.run_checker()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_status_line_is_refused(self):
        self.repo.write(
            ".scratch/effort/issues/01-a.md",
            "Labels: ready-for-agent\n",
        )
        self.repo.stage(".scratch")

        result = self.repo.run_checker()

        self.assert_refused(result, "01-a.md", "no 'Status:' line")

    def test_unknown_status_is_refused(self):
        self.repo.write(
            ".scratch/effort/issues/01-a.md",
            "Status: waiting-for-agent\n",
        )
        self.repo.stage(".scratch")

        result = self.repo.run_checker()

        self.assert_refused(result, "01-a.md", "unknown status 'waiting-for-agent'")

    def test_unknown_label_is_refused(self):
        self.repo.write(
            ".scratch/effort/issues/01-a.md",
            "Labels: urgent\nStatus: awaiting-agent\n",
        )
        self.repo.stage(".scratch")

        result = self.repo.run_checker()

        self.assert_refused(result, "01-a.md", "unknown label 'urgent'")

    def test_closed_ticket_with_another_label_is_refused(self):
        self.repo.write(
            ".scratch/effort/issues/closed/01-a.md",
            "Labels: ready-for-agent\nStatus: done\n",
        )
        self.repo.stage(".scratch")

        result = self.repo.run_checker()

        self.assert_refused(result, "01-a.md", "no label other than 'wontfix'")

    def test_closed_ticket_that_is_not_done_is_refused(self):
        self.repo.write(
            ".scratch/effort/issues/closed/01-a.md",
            "Status: in-review\n",
        )
        self.repo.stage(".scratch")

        result = self.repo.run_checker()

        self.assert_refused(result, "01-a.md", "lives in issues/closed/")

    def test_done_ticket_still_under_issues_is_refused(self):
        self.repo.write(
            ".scratch/effort/issues/01-a.md",
            "Status: done\n",
        )
        self.repo.stage(".scratch")

        result = self.repo.run_checker()

        self.assert_refused(result, "01-a.md", "still under issues/")

    def test_non_utf8_ticket_is_refused_by_name_and_others_are_checked(self):
        self.repo.write(
            ".scratch/effort/issues/01-a.md",
            "Status: awaiting-agent\n".encode("utf-16"),
        )
        self.repo.write(
            ".scratch/effort/issues/02-b.md",
            "Status: waiting-for-agent\n",
        )
        self.repo.stage(".scratch")

        result = self.repo.run_checker()

        self.assert_refused(result, "01-a.md", "UTF-8")
        self.assertNotIn("01-a.md: no 'Status:' line", result.stdout)
        self.assertIn("02-b.md", result.stdout)
        self.assertIn("waiting-for-agent", result.stdout)

    def test_renamed_closed_ticket_is_refused_at_its_new_path(self):
        self.repo.write(
            ".scratch/effort/issues/01-a.md",
            "Status: awaiting-agent\n",
        )
        self.repo.stage(".scratch")
        self.repo.commit()
        self.repo.write(".scratch/effort/issues/closed/.gitkeep", "")
        self.repo.git(
            "mv",
            ".scratch/effort/issues/01-a.md",
            ".scratch/effort/issues/closed/01-a.md",
        )

        result = self.repo.run_checker()

        self.assert_refused(
            result, "issues/closed/01-a.md", "lives in issues/closed/"
        )

    def test_valid_rename_passes(self):
        self.repo.write(
            ".scratch/effort/issues/closed/01-a.md",
            "Status: done\n",
        )
        self.repo.stage(".scratch")
        self.repo.commit()
        self.repo.git(
            "mv",
            ".scratch/effort/issues/closed/01-a.md",
            ".scratch/effort/issues/closed/02-a.md",
        )

        result = self.repo.run_checker()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
