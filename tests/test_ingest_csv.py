import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class IngestCsvWorkflowTest(unittest.TestCase):
    def test_ingest_csv_imports_merges_and_writes_trip(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        trip_path = temp_dir / "trip.json"
        csv_path = temp_dir / "fuel.csv"
        output_path = temp_dir / "ingested-trip.json"

        trip = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))
        trip["travel_days"][0]["fuel_stops"] = []
        trip_path.write_text(json.dumps(trip), encoding="utf-8")
        csv_path.write_text(
            "id,travel_day_id,date,vendor,location,odometer,gallons,total_cost,price_per_gallon,notes\n"
            "fuel-stop-001,sample-day-001,2026-05-01,Example Fuel,Sample Town VA,12345,42.5,165.75,3.9,Sample fuel stop only.\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "ingest-csv",
                "fuel-stop",
                str(trip_path),
                str(csv_path),
                str(output_path),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        merged = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(len(merged["travel_days"][0]["fuel_stops"]), 1)
        self.assertEqual(merged["travel_days"][0]["fuel_stops"][0]["id"], "fuel-stop-001")

    def test_ingest_csv_supports_replace_mode(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        trip_path = temp_dir / "trip.json"
        csv_path = temp_dir / "expenses.csv"
        output_path = temp_dir / "ingested-trip.json"

        trip = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))
        trip["travel_days"][0]["expenses"] = [
            {
                "id": "old-expense",
                "travel_day_id": "sample-day-001",
                "date": "2026-05-01",
                "category": "food",
                "amount": 1.0,
                "vendor": "Old Vendor",
                "notes": "Old note",
            }
        ]
        trip_path.write_text(json.dumps(trip), encoding="utf-8")
        csv_path.write_text(
            "id,travel_day_id,date,category,amount,vendor,notes\n"
            "expense-001,sample-day-001,2026-05-01,food,28.5,Example BBQ,Sanitized restaurant expense.\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "ingest-csv",
                "expense",
                str(trip_path),
                str(csv_path),
                str(output_path),
                "--merge-mode",
                "replace",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        merged = json.loads(output_path.read_text(encoding="utf-8"))
        expenses = merged["travel_days"][0]["expenses"]
        self.assertEqual(expenses[0]["id"], "expense-001")
        self.assertNotEqual(expenses[0]["id"], "old-expense")

    def test_ingest_csv_surfaces_merge_error(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        trip_path = temp_dir / "trip.json"
        csv_path = temp_dir / "bad-fuel.csv"
        output_path = temp_dir / "ingested-trip.json"

        trip = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))
        trip_path.write_text(json.dumps(trip), encoding="utf-8")
        csv_path.write_text(
            "id,travel_day_id,date,vendor,location,odometer,gallons,total_cost,price_per_gallon,notes\n"
            "fuel-bad,missing-day,2026-05-01,Bad Fuel,Nowhere,100,10,30,3,Bad row\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "ingest-csv",
                "fuel-stop",
                str(trip_path),
                str(csv_path),
                str(output_path),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown travel_day_id", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
