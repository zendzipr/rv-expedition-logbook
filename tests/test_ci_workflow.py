import unittest
from pathlib import Path


class CiWorkflowTest(unittest.TestCase):
    def test_ci_workflow_runs_project_checks(self):
        root = Path(__file__).resolve().parents[1]
        workflow = root / ".github" / "workflows" / "ci.yml"
        content = workflow.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/validate.py", content)
        self.assertIn("python3 -m unittest discover -s tests", content)
        self.assertIn("python3 -m rv_logbook render examples/sample-trip.json", content)
        self.assertIn("python3 -m rv_logbook render-html examples/sample-trip.json", content)
        self.assertIn("python3 -m rv_logbook import-csv fuel-stop examples/sample-fuel-stops.csv", content)
        self.assertIn("python3 -m rv_logbook merge-records fuel-stop examples/sample-trip.json examples/sample-fuel-stops-merge.json", content)


if __name__ == "__main__":
    unittest.main()
