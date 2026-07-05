import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class LiveTripWorkspaceTest(unittest.TestCase):
    def test_create_live_trip_workspace_from_rtw(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "create-live-trip",
                "blue-ridge-test",
                "examples/sample-rtw-export.json",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        trip_dir = base_dir / "trips" / "blue-ridge-test"
        self.assertTrue((trip_dir / "trip.json").exists())
        self.assertTrue((trip_dir / "trip.db").exists())
        self.assertTrue((trip_dir / "notes" / "daily-notes.md").exists())
        self.assertTrue((trip_dir / "output").exists())

        trip = json.loads((trip_dir / "trip.json").read_text(encoding="utf-8"))
        self.assertEqual(trip["name"], "Blue Ridge Test Trip")

    def test_add_trip_note_updates_markdown_and_database(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "create-live-trip",
                "blue-ridge-test",
                "examples/sample-rtw-export.json",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "add-trip-note",
                "blue-ridge-test",
                "meal",
                "Great BBQ in Asheville.",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        notes_text = (trip_dir / "notes" / "meal-notes.md").read_text(encoding="utf-8")
        self.assertIn("Great BBQ in Asheville.", notes_text)

        conn = sqlite3.connect(trip_dir / "trip.db")
        try:
            rows = conn.execute("select note_type, content from trip_notes order by id").fetchall()
        finally:
            conn.close()
        self.assertEqual(rows[-1], ("meal", "Great BBQ in Asheville."))

    def test_add_trip_entry_updates_database_and_current_binder(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "create-live-trip", "blue-ridge-test", "examples/sample-rtw-export.json", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        entry = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "add-trip-entry",
                "blue-ridge-test",
                "meal",
                "12 Bones Smokehouse",
                "Best ribs of the trip.",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(entry.returncode, 0, entry.stdout + entry.stderr)

        conn = sqlite3.connect(trip_dir / "trip.db")
        try:
            rows = conn.execute("select entry_type, title, content from trip_entries order by id").fetchall()
        finally:
            conn.close()
        self.assertEqual(rows[-1], ("meal", "12 Bones Smokehouse", "Best ribs of the trip."))

        render = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "render-current-binder", "blue-ridge-test", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(render.returncode, 0, render.stdout + render.stderr)
        binder = (trip_dir / "output" / "current-binder.md").read_text(encoding="utf-8")
        self.assertIn("# Meals", binder)
        self.assertIn("12 Bones Smokehouse", binder)
        self.assertIn("Best ribs of the trip.", binder)

    def test_add_trip_entry_supports_date_and_travel_day_metadata(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "create-live-trip", "blue-ridge-test", "examples/sample-rtw-export.json", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        entry = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "add-trip-entry",
                "blue-ridge-test",
                "fuel",
                "Pilot fill-up",
                "Topped off before the climb.",
                "--date",
                "2026-05-01",
                "--travel-day-id",
                "stop-001",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(entry.returncode, 0, entry.stdout + entry.stderr)

        conn = sqlite3.connect(trip_dir / "trip.db")
        try:
            rows = conn.execute("select entry_type, title, content, occurred_on, travel_day_id from trip_entries order by id").fetchall()
        finally:
            conn.close()
        self.assertEqual(rows[-1], ("fuel", "Pilot fill-up", "Topped off before the climb.", "2026-05-01", "stop-001"))

    def test_add_meal_command_creates_binder_friendly_meal_entry(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "create-live-trip", "blue-ridge-test", "examples/sample-rtw-export.json", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        meal = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "add-meal",
                "blue-ridge-test",
                "12 Bones Smokehouse",
                "Asheville, NC",
                "Best ribs of the trip.",
                "--date",
                "2026-05-01",
                "--travel-day-id",
                "stop-001",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(meal.returncode, 0, meal.stdout + meal.stderr)

        render = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "render-current-binder", "blue-ridge-test", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(render.returncode, 0, render.stdout + render.stderr)
        binder = (trip_dir / "output" / "current-binder.md").read_text(encoding="utf-8")
        self.assertIn("# Meals", binder)
        self.assertIn("12 Bones Smokehouse", binder)
        self.assertIn("Asheville, NC", binder)
        self.assertIn("Best ribs of the trip.", binder)

    def test_add_fuel_stop_command_creates_binder_friendly_fuel_entry(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "create-live-trip", "blue-ridge-test", "examples/sample-rtw-export.json", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        fuel = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "add-fuel-stop",
                "blue-ridge-test",
                "Pilot",
                "Asheville, NC",
                "42.5",
                "165.75",
                "12345",
                "--date",
                "2026-05-01",
                "--travel-day-id",
                "stop-001",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(fuel.returncode, 0, fuel.stdout + fuel.stderr)

        render = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "render-current-binder", "blue-ridge-test", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(render.returncode, 0, render.stdout + render.stderr)
        binder = (trip_dir / "output" / "current-binder.md").read_text(encoding="utf-8")
        self.assertIn("# Fuel & Mileage", binder)
        self.assertIn("Pilot", binder)
        self.assertIn("42.5 gallons", binder)
        self.assertIn("$165.75", binder)
        self.assertIn("Odometer: 12345", binder)

    def test_add_stop_command_creates_binder_friendly_stop_entry(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "create-live-trip", "blue-ridge-test", "examples/sample-rtw-export.json", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        stop = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "add-stop",
                "blue-ridge-test",
                "Biltmore Estate",
                "Asheville, NC",
                "Great detour and worth the ticket price.",
                "--date",
                "2026-05-01",
                "--travel-day-id",
                "stop-001",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(stop.returncode, 0, stop.stdout + stop.stderr)

        render = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "render-current-binder", "blue-ridge-test", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(render.returncode, 0, render.stdout + render.stderr)
        binder = (trip_dir / "output" / "current-binder.md").read_text(encoding="utf-8")
        self.assertIn("# Stops", binder)
        self.assertIn("Biltmore Estate", binder)
        self.assertIn("Asheville, NC", binder)
        self.assertIn("worth the ticket price", binder)

    def test_add_campground_review_command_creates_binder_friendly_review(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "create-live-trip", "blue-ridge-test", "examples/sample-rtw-export.json", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        campground = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "add-campground-review",
                "blue-ridge-test",
                "Sample Campground",
                "Site 12",
                "4.5",
                "yes",
                "Quiet site, strong hookups, would gladly return.",
                "--date",
                "2026-05-01",
                "--travel-day-id",
                "stop-001",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(campground.returncode, 0, campground.stdout + campground.stderr)

        render = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "render-current-binder", "blue-ridge-test", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(render.returncode, 0, render.stdout + render.stderr)
        binder = (trip_dir / "output" / "current-binder.md").read_text(encoding="utf-8")
        self.assertIn("# Campgrounds", binder)
        self.assertIn("Sample Campground", binder)
        self.assertIn("Site 12", binder)
        self.assertIn("Rating: 4.5/5", binder)
        self.assertIn("Would return: yes", binder)

    def test_current_binder_groups_entries_into_binder_sections(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "create-live-trip", "blue-ridge-test", "examples/sample-rtw-export.json", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        for args in [
            ["add-trip-entry", "blue-ridge-test", "meal", "12 Bones Smokehouse", "Best ribs of the trip.", "--base-dir", str(base_dir)],
            ["add-trip-entry", "blue-ridge-test", "fuel", "Pilot fill-up", "Topped off before the climb.", "--date", "2026-05-01", "--travel-day-id", "stop-001", "--base-dir", str(base_dir)],
        ]:
            result = subprocess.run([sys.executable, "-m", "rv_logbook", *args], cwd=root, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        render = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "render-current-binder", "blue-ridge-test", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(render.returncode, 0, render.stdout + render.stderr)
        binder = (trip_dir / "output" / "current-binder.md").read_text(encoding="utf-8")
        self.assertIn("# Meals", binder)
        self.assertIn("# Fuel & Mileage", binder)
        self.assertIn("Pilot fill-up", binder)
        self.assertIn("Travel day: stop-001", binder)

    def test_trip_questions_reports_missing_follow_up_areas(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"

        create = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "create-live-trip", "blue-ridge-test", "examples/sample-rtw-export.json", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        questions = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "trip-questions", "blue-ridge-test", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(questions.returncode, 0, questions.stdout + questions.stderr)
        self.assertIn("What meals were memorable", questions.stdout)
        self.assertIn("Any memorable stops", questions.stdout)

    def test_finalize_trip_generates_final_binder_and_marks_trip_complete(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "create-live-trip", "blue-ridge-test", "examples/sample-rtw-export.json", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        reflection = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "add-final-reflection",
                "blue-ridge-test",
                "Loved the Blue Ridge stretch and would stay longer next time.",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(reflection.returncode, 0, reflection.stdout + reflection.stderr)

        finalize = subprocess.run(
            [sys.executable, "-m", "rv_logbook", "finalize-trip", "blue-ridge-test", "--base-dir", str(base_dir)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(finalize.returncode, 0, finalize.stdout + finalize.stderr)

        trip = json.loads((trip_dir / "trip.json").read_text(encoding="utf-8"))
        self.assertEqual(trip.get("status"), "complete")
        self.assertTrue((trip_dir / "output" / "final-binder.md").exists())
        binder = (trip_dir / "output" / "final-binder.md").read_text(encoding="utf-8")
        self.assertIn("Final Reflections", binder)
        self.assertIn("Loved the Blue Ridge stretch", binder)

        conn = sqlite3.connect(trip_dir / "trip.db")
        try:
            rows = conn.execute("select content from final_reflections order by id").fetchall()
        finally:
            conn.close()
        self.assertEqual(rows[-1][0], "Loved the Blue Ridge stretch and would stay longer next time.")

    def test_render_current_binder_writes_workspace_output(self):
        root = Path(__file__).resolve().parents[1]
        temp_dir = Path(tempfile.mkdtemp())
        base_dir = temp_dir / "data"
        trip_dir = base_dir / "trips" / "blue-ridge-test"

        create = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "create-live-trip",
                "blue-ridge-test",
                "examples/sample-rtw-export.json",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(create.returncode, 0, create.stdout + create.stderr)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rv_logbook",
                "render-current-binder",
                "blue-ridge-test",
                "--base-dir",
                str(base_dir),
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        binder_path = trip_dir / "output" / "current-binder.md"
        self.assertTrue(binder_path.exists())
        binder = binder_path.read_text(encoding="utf-8")
        self.assertIn("Blue Ridge Test Trip", binder)


if __name__ == "__main__":
    unittest.main()
