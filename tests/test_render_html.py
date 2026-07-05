import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RenderHtmlTest(unittest.TestCase):
    def test_module_cli_renders_html_report(self):
        root = Path(__file__).resolve().parents[1]
        output_file = Path(tempfile.mkdtemp()) / "sample-report.html"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "render-html",
                "examples/sample-trip.json",
                str(output_file),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        rendered = output_file.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", rendered)
        self.assertIn("Sample Blue Ridge Weekend", rendered)
        self.assertIn("Trip Summary", rendered)
        self.assertIn("Travel Day", rendered)
        self.assertIn("Fuel Stops", rendered)
        self.assertIn("Expenses", rendered)

    def test_html_renderer_fails_for_missing_required_trip_fields(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        bad_input = temp_dir / "bad-trip.json"
        bad_input.write_text(json.dumps({"id": "missing-name"}), encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "render-html",
                str(bad_input),
                str(temp_dir / "out.html"),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required field", result.stderr)


if __name__ == "__main__":
    unittest.main()
