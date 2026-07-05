from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .render import BinderRenderError, fail, load_json, render_binder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rv_logbook", description="RV Expedition Logbook tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="render a Markdown binder from trip JSON")
    render_parser.add_argument("input", help="input trip JSON file")
    render_parser.add_argument("output", help="output Markdown file")
    return parser


def render_command(input_path: str, output_path: str) -> int:
    trip = load_json(Path(input_path))
    try:
        rendered = render_binder(trip)
    except BinderRenderError as exc:
        fail(str(exc))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")
    print(f"Rendered binder: {destination}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "render":
        return render_command(args.input, args.output)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
