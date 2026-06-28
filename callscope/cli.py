"""Command-line interface for callscope."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from callscope.analyzer import analyze
from callscope.models import CallReport


def _analyze_paths(paths: List[Path], fmt: str) -> List[CallReport]:
    reports: List[CallReport] = []
    for p in paths:
        report = analyze(p.read_text(encoding="utf-8"), fmt=fmt)
        if report.call_id is None:
            report.call_id = p.stem
        reports.append(report)
    return reports


def _print_summary(reports: List[CallReport]) -> None:
    width = max((len(str(r.call_id)) for r in reports), default=8)
    print(f"{'CALL'.ljust(width)}  {'OUTCOME'.ljust(14)}  SCORE  EVENTS")
    print("-" * (width + 34))
    for r in reports:
        events = ", ".join(r.events) or "-"
        print(f"{str(r.call_id).ljust(width)}  {r.outcome.ljust(14)}  {str(r.score).rjust(5)}  {events}")
    n = len(reports)
    if n:
        human = sum(1 for r in reports if r.outcome == "human_reached")
        booked = sum(1 for r in reports if "appointment_booked" in r.events)
        avg = round(sum(r.score for r in reports) / n, 1)
        print("-" * (width + 34))
        print(f"{n} call(s) | {human} reached a human | {booked} booked | avg score {avg}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="callscope",
        description="Outcome analytics and quality scoring for AI voice-agent calls.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("analyze", help="Analyze one or more transcript files.")
    a.add_argument("paths", nargs="+", type=Path, help="Transcript files (JSON or text).")
    a.add_argument("--format", default="auto", choices=["auto", "vapi", "text"])
    a.add_argument("--out", type=Path, help="Write the full JSON report to this path.")
    args = parser.parse_args(argv)

    if args.command == "analyze":
        reports = _analyze_paths(args.paths, args.format)
        _print_summary(reports)
        if args.out:
            args.out.write_text(
                json.dumps([r.to_dict() for r in reports], indent=2), encoding="utf-8"
            )
            print(f"\nWrote {len(reports)} report(s) to {args.out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
