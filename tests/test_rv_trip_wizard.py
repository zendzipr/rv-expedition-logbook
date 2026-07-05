import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class RvTripWizardImportTest(unittest.TestCase):
    def test_import_rtw_json_outputs_normalized_trip(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        input_file = temp_dir / "rtw-export.json"
        output_file = temp_dir / "trip.json"

        input_file.write_text(
            json.dumps(
                {
                    "trip_name": "Blue Ridge Test Trip",
                    "start_date": "2026-05-01",
                    "end_date": "2026-05-03",
                    "stops": [
                        {
                            "stop_id": "stop-001",
                            "date": "2026-05-01",
                            "name": "Sample Campground",
                            "location": "Western North Carolina",
                            "site": "12",
                            "nightly_cost": 45.0,
                            "distance_miles": 210,
                            "route_notes": "Mountain grades required slower driving.",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "import-rtw",
                str(input_file),
                str(output_file),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        trip = json.loads(output_file.read_text(encoding="utf-8"))
        self.assertEqual(trip["name"], "Blue Ridge Test Trip")
        self.assertEqual(trip["provenance"]["source"], "rv-trip-wizard")
        self.assertEqual(len(trip["travel_days"]), 1)
        self.assertEqual(trip["travel_days"][0]["campground"]["name"], "Sample Campground")
        self.assertEqual(trip["travel_days"][0]["miles"], 210)
        self.assertEqual(trip["travel_days"][0]["expenses"][0]["amount"], 45.0)

    def test_import_rtw_rejects_missing_stop_date(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        input_file = temp_dir / "bad-rtw-export.json"
        output_file = temp_dir / "trip.json"

        input_file.write_text(
            json.dumps(
                {
                    "trip_name": "Broken Trip",
                    "start_date": "2026-05-01",
                    "stops": [
                        {
                            "stop_id": "stop-001",
                            "name": "Sample Campground"
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "import-rtw",
                str(input_file),
                str(output_file),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stop", result.stderr.lower())
        self.assertIn("date", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
