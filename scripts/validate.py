#!/usr/bin/env python3
"""Validate repository assets, schemas, examples, skill, and templates."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rv_logbook.schema import SchemaValidationError, validate_repository


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}")
    raise SystemExit(1)


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
    try:
        checked = validate_repository()
    except SchemaValidationError as exc:
        fail(str(exc))
    for item in checked:
        print(f"OK schema: {item}")
    validate_skill()
    validate_templates()
    print("Validation complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
