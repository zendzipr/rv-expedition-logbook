import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MergeRecordsTest(unittest.TestCase):
    def test_merge_records_attaches_fuel_stops_to_matching_travel_day(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        trip_path = temp_dir / "trip.json"
        imported_path = temp_dir / "fuel.json"
        output_path = temp_dir / "merged.json"

        trip = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))
        trip["travel_days"][0]["fuel_stops"] = []
        trip_path.write_text(json.dumps(trip), encoding="utf-8")
        imported_path.write_text(
            json.dumps(
                [
                    {
                        "id": "fuel-stop-merge-001",
                        "travel_day_id": "sample-day-001",
                        "date": "2026-05-01",
                        "vendor": "Merge Fuel",
                        "location": "Merge Town",
                        "odometer": 13000,
                        "gallons": 25.0,
                        "total_cost": 100.0,
                        "price_per_gallon": 4.0,
                        "notes": "Merged fuel stop.",
                    }
                ]
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "merge-records",
                "fuel-stop",
                str(trip_path),
                str(imported_path),
                str(output_path),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        merged = json.loads(output_path.read_text(encoding="utf-8"))
        fuel_stops = merged["travel_days"][0]["fuel_stops"]
        self.assertEqual(len(fuel_stops), 1)
        self.assertEqual(fuel_stops[0]["id"], "fuel-stop-merge-001")
        self.assertEqual(fuel_stops[0]["travel_day_id"], "sample-day-001")

    def test_merge_records_attaches_expenses_without_clobbering_existing_fields(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        trip_path = temp_dir / "trip.json"
        imported_path = temp_dir / "expenses.json"
        output_path = temp_dir / "merged.json"

        trip = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))
        trip["travel_days"][0]["expenses"] = []
        trip_path.write_text(json.dumps(trip), encoding="utf-8")
        imported_path.write_text(
            json.dumps(
                [
                    {
                        "id": "expense-merge-001",
                        "travel_day_id": "sample-day-001",
                        "date": "2026-05-01",
                        "category": "supplies",
                        "amount": 15.25,
                        "vendor": "Example Store",
                        "notes": "Merged expense.",
                    }
                ]
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "merge-records",
                "expense",
                str(trip_path),
                str(imported_path),
                str(output_path),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        merged = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(merged["name"], "Sample Blue Ridge Weekend")
        expenses = merged["travel_days"][0]["expenses"]
        self.assertEqual(expenses[0]["category"], "supplies")
        self.assertEqual(expenses[0]["amount"], 15.25)

    def test_merge_records_replace_mode_replaces_existing_records(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        trip_path = temp_dir / "trip.json"
        imported_path = temp_dir / "fuel.json"
        output_path = temp_dir / "merged.json"

        trip = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))
        trip["travel_days"][0]["fuel_stops"] = [
            {
                "id": "old-fuel-stop",
                "travel_day_id": "sample-day-001",
                "date": "2026-05-01",
                "vendor": "Old Fuel",
                "location": "Old Town",
                "odometer": 12000,
                "gallons": 10.0,
                "total_cost": 30.0,
                "price_per_gallon": 3.0,
                "notes": "Old record.",
            }
        ]
        trip_path.write_text(json.dumps(trip), encoding="utf-8")
        imported_path.write_text(
            json.dumps(
                [
                    {
                        "id": "new-fuel-stop",
                        "travel_day_id": "sample-day-001",
                        "date": "2026-05-01",
                        "vendor": "New Fuel",
                        "location": "New Town",
                        "odometer": 13000,
                        "gallons": 20.0,
                        "total_cost": 80.0,
                        "price_per_gallon": 4.0,
                        "notes": "Replacement record.",
                    }
                ]
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "merge-records",
                "fuel-stop",
                str(trip_path),
                str(imported_path),
                str(output_path),
                "--mode",
                "replace",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        merged = json.loads(output_path.read_text(encoding="utf-8"))
        fuel_stops = merged["travel_days"][0]["fuel_stops"]
        self.assertEqual([record["id"] for record in fuel_stops], ["new-fuel-stop"])

    def test_merge_records_rejects_duplicate_ids_in_append_mode(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        trip_path = temp_dir / "trip.json"
        imported_path = temp_dir / "fuel.json"
        output_path = temp_dir / "merged.json"

        trip = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))
        trip["travel_days"][0]["fuel_stops"] = [
            {
                "id": "dup-fuel-stop",
                "travel_day_id": "sample-day-001",
                "date": "2026-05-01",
                "vendor": "Existing Fuel",
                "location": "Old Town",
                "odometer": 12000,
                "gallons": 10.0,
                "total_cost": 30.0,
                "price_per_gallon": 3.0,
                "notes": "Existing record.",
            }
        ]
        trip_path.write_text(json.dumps(trip), encoding="utf-8")
        imported_path.write_text(
            json.dumps(
                [
                    {
                        "id": "dup-fuel-stop",
                        "travel_day_id": "sample-day-001",
                        "date": "2026-05-01",
                        "vendor": "Duplicate Fuel",
                        "location": "Dup Town",
                        "odometer": 13000,
                        "gallons": 20.0,
                        "total_cost": 80.0,
                        "price_per_gallon": 4.0,
                        "notes": "Duplicate record.",
                    }
                ]
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "merge-records",
                "fuel-stop",
                str(trip_path),
                str(imported_path),
                str(output_path),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate record id", result.stderr.lower())

    def test_merge_records_rejects_unknown_travel_day(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        trip_path = temp_dir / "trip.json"
        imported_path = temp_dir / "fuel.json"
        output_path = temp_dir / "merged.json"

        trip = json.loads((root / "examples" / "sample-trip.json").read_text(encoding="utf-8"))
        trip_path.write_text(json.dumps(trip), encoding="utf-8")
        imported_path.write_text(
            json.dumps(
                [
                    {
                        "id": "fuel-stop-merge-999",
                        "travel_day_id": "missing-day",
                        "date": "2026-05-01",
                        "vendor": "Nowhere Fuel",
                        "location": "Nowhere",
                        "odometer": 13000,
                        "gallons": 25.0,
                        "total_cost": 100.0,
                        "price_per_gallon": 4.0,
                        "notes": "Bad day id.",
                    }
                ]
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "merge-records",
                "fuel-stop",
                str(trip_path),
                str(imported_path),
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
