"""Command-line interface for callscope."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from callscope.analyzer import analyze
from callscope.models import CallReport

_SUPPORTED_INPUTS = {".json", ".txt"}


def _expand_paths(paths: Iterable[Path]) -> List[Path]:
    """Expand files and directories into a stable transcript file list."""
    expanded: List[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(
                sorted(
                    child
                    for child in path.rglob("*")
                    if child.is_file() and child.suffix.lower() in _SUPPORTED_INPUTS
                )
            )
        else:
            expanded.append(path)
    return expanded


def _analyze_paths(paths: List[Path], fmt: str) -> List[CallReport]:
    reports: List[CallReport] = []
    for p in _expand_paths(paths):
        report = analyze(p.read_text(encoding="utf-8"), fmt=fmt)
        if report.call_id is None:
            report.call_id = p.stem
        reports.append(report)
    return reports


def _write_json(reports: List[CallReport], path: Path) -> None:
    path.write_text(json.dumps([r.to_dict() for r in reports], indent=2), encoding="utf-8")


def _write_jsonl(reports: List[CallReport], path: Path) -> None:
    lines = [json.dumps(r.to_dict(), sort_keys=True) for r in reports]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _write_csv(reports: List[CallReport], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "call_id",
                "outcome",
                "score",
                "events",
                "turns",
                "customer_turns",
                "customer_talk_ratio",
                "agent_words",
                "customer_words",
                "source",
            ],
        )
        writer.writeheader()
        for r in reports:
            writer.writerow(
                {
                    "call_id": r.call_id or "",
                    "outcome": r.outcome,
                    "score": r.score,
                    "events": ";".join(r.events),
                    "turns": r.metrics.get("turns", 0),
                    "customer_turns": r.metrics.get("customer_turns", 0),
                    "customer_talk_ratio": r.metrics.get("customer_talk_ratio", 0),
                    "agent_words": r.metrics.get("agent_words", 0),
                    "customer_words": r.metrics.get("customer_words", 0),
                    "source": r.source,
                }
            )


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


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"{path}:{line_no}: expected an object")
        cases.append(item)
    return cases


def _case_transcript(case: Dict[str, Any]) -> Any:
    if "transcript" in case:
        return case["transcript"]
    if "messages" in case:
        return {"id": case.get("id"), "messages": case["messages"]}
    raise ValueError(f"benchmark case {case.get('id', '<missing id>')} needs transcript or messages")


def _run_benchmark(path: Path) -> int:
    cases = _read_jsonl(path)
    rows: List[Dict[str, Any]] = []
    failures = 0
    total_expected_events = 0
    hit_expected_events = 0

    for i, case in enumerate(cases, start=1):
        case_id = str(case.get("id") or f"case_{i:03d}")
        expected_outcome = str(case["expected_outcome"])
        expected_events: Set[str] = set(case.get("expected_events", []))
        report = analyze(_case_transcript(case), fmt=str(case.get("format", "auto")))
        actual_events = set(report.events)
        missing_events = sorted(expected_events - actual_events)
        outcome_ok = report.outcome == expected_outcome
        event_ok = not missing_events
        status = "ok" if outcome_ok and event_ok else "fail"
        if status == "fail":
            failures += 1
        total_expected_events += len(expected_events)
        hit_expected_events += len(expected_events & actual_events)
        rows.append(
            {
                "id": case_id,
                "expected": expected_outcome,
                "actual": report.outcome,
                "score": report.score,
                "events": ",".join(report.events) or "-",
                "missing": ",".join(missing_events) or "-",
                "status": status,
            }
        )

    width = max((len(r["id"]) for r in rows), default=4)
    print(f"{'CASE'.ljust(width)}  EXPECTED       ACTUAL         SCORE  STATUS  MISSING")
    print("-" * (width + 58))
    for r in rows:
        print(
            f"{r['id'].ljust(width)}  {r['expected'].ljust(13)}  "
            f"{r['actual'].ljust(13)}  {str(r['score']).rjust(5)}  {r['status'].ljust(6)}  {r['missing']}"
        )
    passed = len(rows) - failures
    event_rate = round(hit_expected_events / total_expected_events, 3) if total_expected_events else 1.0
    print("-" * (width + 58))
    print(f"{passed}/{len(rows)} cases passed | expected-event recall {event_rate}")
    return 0 if failures == 0 else 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="callscope",
        description="Outcome analytics and quality scoring for AI voice-agent calls.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("analyze", help="Analyze one or more transcript files or folders.")
    a.add_argument("paths", nargs="+", type=Path, help="Transcript files or folders of JSON/TXT files.")
    a.add_argument("--format", default="auto", choices=["auto", "vapi", "text"])
    a.add_argument("--out", type=Path, help="Write the full JSON report to this path.")
    a.add_argument("--csv", type=Path, help="Write a spreadsheet-friendly CSV summary.")
    a.add_argument("--jsonl", type=Path, help="Write one JSON report per line.")

    b = sub.add_parser("benchmark", help="Run a JSONL benchmark of expected outcomes and events.")
    b.add_argument("path", type=Path, help="JSONL benchmark file.")
    args = parser.parse_args(argv)

    if args.command == "analyze":
        reports = _analyze_paths(args.paths, args.format)
        _print_summary(reports)
        if args.out:
            _write_json(reports, args.out)
            print(f"\nWrote {len(reports)} report(s) to {args.out}")
        if args.csv:
            _write_csv(reports, args.csv)
            print(f"Wrote {len(reports)} CSV row(s) to {args.csv}")
        if args.jsonl:
            _write_jsonl(reports, args.jsonl)
            print(f"Wrote {len(reports)} JSONL row(s) to {args.jsonl}")
        return 0
    if args.command == "benchmark":
        return _run_benchmark(args.path)
    return 1


if __name__ == "__main__":
    sys.exit(main())
