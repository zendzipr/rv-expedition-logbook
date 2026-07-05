import subprocess
import sys
import unittest
from pathlib import Path


class ValidateScriptTest(unittest.TestCase):
    def test_validate_script_runs(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "validate.py")],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
