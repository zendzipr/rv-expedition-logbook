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
        self.assertIn("Live Trip Entries", binder)
        self.assertIn("12 Bones Smokehouse", binder)
        self.assertIn("Best ribs of the trip.", binder)

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
