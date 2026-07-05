"""Launch-readiness audit for callscope."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def text(path: str) -> str:
    p = ROOT / path
    if not p.exists():
        fail(f"missing {path}")
    return p.read_text(encoding="utf-8-sig")


def has(path: str, needles: list[str]) -> None:
    body = text(path)
    missing = [needle for needle in needles if needle not in body]
    if missing:
        fail(f"{path} missing {missing}")


def count_jsonl(path: str) -> int:
    count = 0
    for line_no, line in enumerate(text(path).splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"{path}:{line_no} invalid JSONL: {exc}")
        count += 1
    return count


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout)
    if result.returncode != 0:
        fail(f"command failed: {' '.join(command)}")


def main() -> int:
    has("README.md", [
        "python -m callscope analyze examples --csv report.csv --jsonl report.jsonl",
        "python -m callscope benchmark benchmark/calls.jsonl",
        "docs/BENCHMARK.md",
        "docs/EXPORTS.md",
        "docs/assets/terminal-demo.svg",
        "Star this repo if",
    ])
    has("docs/GITHUB_SETUP.md", ["voice-ai", "call-analytics", "vapi", "retell", "twilio"])
    has(".github/workflows/launch-ready.yml", ["schedule:", "python -m callscope benchmark benchmark/calls.jsonl", "python scripts/launch_audit.py"])
    cases = count_jsonl("benchmark/calls.jsonl")
    if cases < 20:
        fail(f"benchmark too small: {cases}")
    run([sys.executable, "-m", "callscope", "benchmark", "benchmark/calls.jsonl"])
    print(f"OK: launch surfaces ready, benchmark_cases={cases}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
