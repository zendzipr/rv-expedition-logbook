#!/usr/bin/env python3
"""Lightweight repository validation with no third-party dependencies."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def validate_json_files() -> None:
    for path in sorted((ROOT / "schemas").glob("*.json")) + sorted((ROOT / "examples").glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - validation script should report any parse issue
            fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        print(f"OK json: {path.relative_to(ROOT)}")


def validate_skill() -> None:
    skill_path = ROOT / "skills" / "rv-expedition-logbook" / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")

    match = re.search(r"\n---\s*\n", content[4:])
    if not match:
        fail("SKILL.md frontmatter is not closed")

    close_start = 4 + match.start()
    close_end = 4 + match.end()
    frontmatter = content[4:close_start]
    body = content[close_end:].strip()
    if not body:
        fail("SKILL.md body is empty")

    for field in ("name:", "description:", "version:", "author:", "license:"):
        if field not in frontmatter:
            fail(f"SKILL.md missing {field}")

    description_line = next((line for line in frontmatter.splitlines() if line.startswith("description:")), "")
    if len(description_line.partition(":")[2].strip()) > 1024:
        fail("SKILL.md description is too long")

    print("OK skill: skills/rv-expedition-logbook/SKILL.md")


def validate_templates() -> None:
    paths = sorted((ROOT / "templates" / "binder").glob("*.md"))
    if not paths:
        fail("no binder templates found")
    for path in paths:
        text = path.read_text(encoding="utf-8").strip()
        if not text.startswith("#"):
            fail(f"template should start with a heading: {path.relative_to(ROOT)}")
        print(f"OK template: {path.relative_to(ROOT)}")


def main() -> int:
    validate_json_files()
    validate_skill()
    validate_templates()
    print("Validation complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
