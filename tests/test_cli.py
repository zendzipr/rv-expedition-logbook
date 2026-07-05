import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class PackageCliTest(unittest.TestCase):
    def test_module_cli_renders_binder(self):
        root = Path(__file__).resolve().parents[1]
        output_file = Path(tempfile.mkdtemp()) / "binder.md"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "render",
                "examples/sample-trip.json",
                str(output_file),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Rendered binder:", result.stdout)
        rendered = output_file.read_text(encoding="utf-8")
        self.assertIn("# Sample Blue Ridge Weekend", rendered)
        self.assertIn("# Fuel Log", rendered)

    def test_module_cli_rejects_unknown_command(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "nonsense"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage:", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
