import unittest
from pathlib import Path


class SkillAssetsTest(unittest.TestCase):
    def test_rv_logbook_skill_is_self_contained(self):
        root = Path(__file__).resolve().parents[1]
        skill_dir = root / "skills" / "rv-expedition-logbook"
        skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

        expected_templates = [
            "templates/binder/cover.md",
            "templates/binder/trip-summary.md",
            "templates/binder/travel-day-dashboard.md",
            "templates/binder/campground-review.md",
            "templates/binder/fuel-log.md",
            "templates/binder/expense-log.md",
            "templates/binder/maintenance-log.md",
            "templates/binder/captain-log.md",
        ]

        for rel_path in expected_templates:
            self.assertTrue((skill_dir / rel_path).exists(), rel_path)
            self.assertIn(f"`{rel_path}`", skill_md)

        self.assertNotIn("repository templates", skill_md.lower())


if __name__ == "__main__":
    unittest.main()
