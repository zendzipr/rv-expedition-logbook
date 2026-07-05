import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RenderBinderTest(unittest.TestCase):
    def test_sample_trip_generates_markdown_binder(self):
        root = Path(__file__).resolve().parents[1]
        output_dir = Path(tempfile.mkdtemp())
        output_file = output_dir / "sample-binder.md"

        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "render_binder.py"),
                str(root / "examples" / "sample-trip.json"),
                str(output_file),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        rendered = output_file.read_text(encoding="utf-8")
        self.assertIn("# Sample Blue Ridge Weekend", rendered)
        self.assertIn("# Trip Summary: Sample Blue Ridge Weekend", rendered)
        self.assertIn("# Travel Day: 2026-05-01", rendered)
        self.assertIn("Sample City, VA", rendered)
        self.assertIn("Sample Campground, NC", rendered)
        self.assertIn("Start earlier on Friday travel days.", rendered)

    def test_renderer_fails_for_missing_required_trip_fields(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        bad_input = temp_dir / "bad-trip.json"
        bad_input.write_text(json.dumps({"id": "missing-name"}), encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "render_binder.py"),
                str(bad_input),
                str(temp_dir / "out.md"),
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
