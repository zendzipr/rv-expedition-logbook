import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CsvImportTest(unittest.TestCase):
    def test_import_csv_fuel_stop_outputs_json_records(self):
        root = Path(__file__).resolve().parents[1]
        output_file = Path(tempfile.mkdtemp()) / "fuel.json"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "import-csv",
                "fuel-stop",
                "examples/sample-fuel-stops.csv",
                str(output_file),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(output_file.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], "fuel-stop-001")
        self.assertEqual(data[0]["vendor"], "Example Fuel")
        self.assertEqual(data[0]["travel_day_id"], "sample-day-001")
        self.assertEqual(data[1]["gallons"], 20.0)

    def test_import_csv_expense_outputs_json_records(self):
        root = Path(__file__).resolve().parents[1]
        output_file = Path(tempfile.mkdtemp()) / "expenses.json"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "import-csv",
                "expense",
                "examples/sample-expenses.csv",
                str(output_file),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(output_file.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["category"], "food")
        self.assertEqual(data[1]["amount"], 45.0)

    def test_import_csv_rejects_missing_required_column(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        bad_csv = temp_dir / "bad.csv"
        bad_csv.write_text("id,date\nbad-1,2026-05-01\n", encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "import-csv",
                "expense",
                str(bad_csv),
                str(temp_dir / "out.json"),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required columns", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
