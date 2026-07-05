import unittest
from pathlib import Path


class BinderFirstFramingTest(unittest.TestCase):
    def test_live_trip_workspace_doc_exists(self):
        root = Path(__file__).resolve().parents[1]
        content = (root / "docs" / "LIVE_TRIP_WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("data/trips/<trip-slug>/", content)
        self.assertIn("current binder snapshot", content.lower())
        self.assertIn("final binder", content.lower())

    def test_data_trips_directory_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "data" / "trips" / ".gitkeep").exists())

    def test_readme_emphasizes_binder_first(self):
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("binder-first", readme)
        self.assertIn("live trip binder", readme)


if __name__ == "__main__":
    unittest.main()
