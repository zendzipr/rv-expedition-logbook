import subprocess
import sys
import unittest
from pathlib import Path
import tomllib


class PackagingMetadataTest(unittest.TestCase):
    def test_pyproject_declares_package_and_cli(self):
        root = Path(__file__).resolve().parents[1]
        pyproject = root / "pyproject.toml"
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))

        self.assertEqual(data["project"]["name"], "rv-expedition-logbook")
        self.assertIn("jsonschema", "\n".join(data["project"]["dependencies"]))
        self.assertEqual(data["project"]["scripts"]["rv-logbook"], "rv_logbook.__main__:main")

    def test_package_help_runs(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "--help"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("validate", result.stdout)
        self.assertIn("render", result.stdout)


if __name__ == "__main__":
    unittest.main()
