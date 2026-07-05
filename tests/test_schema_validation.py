import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class SchemaValidationTest(unittest.TestCase):
    def test_validate_command_accepts_sample_trip(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "validate", "examples/sample-trip.json", "--schema", "trip"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("valid", result.stdout.lower())

    def test_validate_command_rejects_invalid_trip(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        bad_trip = temp_dir / "bad-trip.json"
        bad_trip.write_text(json.dumps({"id": "bad", "start_date": "2026-05-01"}), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "validate", str(bad_trip), "--schema", "trip"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("name", result.stderr)

    def test_validate_repository_command_checks_examples_and_schemas(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "validate-repo"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("repository validation complete", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
