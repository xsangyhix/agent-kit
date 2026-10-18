"""Packaging check: the installed wheel carries the whole payload (ticket 08)."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = REPO_ROOT / "src" / "agent_kit" / "payload"
WHEEL_PREFIX = "agent_kit/payload/"


@unittest.skipIf(
    os.environ.get("SKIP_PACKAGING_TEST"),
    "SKIP_PACKAGING_TEST is set",
)
class PackagingTests(unittest.TestCase):
    def test_wheel_contains_every_payload_file(self):
        expected = sorted(
            path.relative_to(PAYLOAD).as_posix()
            for path in PAYLOAD.rglob("*")
            if path.is_file()
        )

        with tempfile.TemporaryDirectory() as folder:
            tmp = Path(folder)
            project = tmp / "project"
            _copy_project(project)
            wheel_dir = tmp / "wheel"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "wheel",
                    ".",
                    "--no-deps",
                    "-w",
                    str(wheel_dir),
                ],
                cwd=project,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                result.returncode, 0, result.stdout + result.stderr
            )

            wheels = list(wheel_dir.glob("*.whl"))
            self.assertEqual(len(wheels), 1, wheels)

            with zipfile.ZipFile(wheels[0]) as wheel:
                shipped = sorted(
                    name[len(WHEEL_PREFIX) :]
                    for name in wheel.namelist()
                    if name.startswith(WHEEL_PREFIX)
                )

        self.assertEqual(shipped, expected)
        for name in ("kit/hooks/pre-commit", "skills/LICENSE", "skills/UPSTREAM"):
            self.assertIn(name, shipped)


def _copy_project(destination):
    """Copy the project into a clean folder, without local build artefacts."""
    destination.mkdir(parents=True)
    shutil.copyfile(REPO_ROOT / "pyproject.toml", destination / "pyproject.toml")
    shutil.copyfile(REPO_ROOT / "README.md", destination / "README.md")
    shutil.copytree(
        REPO_ROOT / "src",
        destination / "src",
        ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"),
    )
