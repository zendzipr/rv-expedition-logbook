import subprocess
import sys
import unittest
from pathlib import Path
import tomllib


class ReleaseArtifactsTest(unittest.TestCase):
    def test_changelog_contains_v0_1_0_entry(self):
        root = Path(__file__).resolve().parents[1]
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## v0.1.0", changelog)
        self.assertIn("installable Python package", changelog)
        self.assertIn("Markdown and HTML rendering", changelog)

    def test_makefile_exposes_common_targets(self):
        root = Path(__file__).resolve().parents[1]
        makefile = (root / "Makefile").read_text(encoding="utf-8")
        for target in ["validate:", "test:", "render-sample:", "render-html-sample:", "ingest-sample:"]:
            self.assertIn(target, makefile)

    def test_end_to_end_doc_mentions_pipeline(self):
        root = Path(__file__).resolve().parents[1]
        content = (root / "docs" / "END_TO_END_EXAMPLE.md").read_text(encoding="utf-8")
        self.assertIn("import-csv", content)
        self.assertIn("merge-records", content)
        self.assertIn("render-html", content)

    def test_make_validate_target_runs(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["make", "validate"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_make_test_target_expands_expected_command(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["make", "-n", "test"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-m unittest discover -s tests", result.stdout)


if __name__ == "__main__":
    unittest.main()
