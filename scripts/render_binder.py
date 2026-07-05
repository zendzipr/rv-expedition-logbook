#!/usr/bin/env python3
"""Compatibility wrapper for `python3 -m rv_logbook render`."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rv_logbook.__main__ import render_command


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: render_binder.py <trip.json> <output.md>", file=sys.stderr)
        return 2
    return render_command(argv[1], argv[2])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
