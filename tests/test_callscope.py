"""Tests for callscope. Run with ``pytest`` or ``python tests/test_callscope.py``."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from callscope import analyze, parse_transcript  # noqa: E402


def test_human_conversation_with_booking():
    text = """
    Agent: Hi, this is Leon with Core Dispatch, who am I speaking with?
    Customer: This is Mike, what's this about?
    Agent: We answer missed calls for shops like yours. How do you handle after-hours calls?
    Customer: Honestly they just go to voicemail. How much is it?
    Agent: A hundred forty nine a month. Want me to set it up?
    Customer: Yeah let's do it, what time can you call me tomorrow?
    """
    r = analyze(text, fmt="text")
    assert r.outcome == "human_reached"
    assert "appointment_booked" in r.events
    assert "price_discussed" in r.events
    assert r.score >= 80


def test_voicemail_detected():
    text = """
    Agent: Hello?
    Customer: Please leave a message after the tone.
    """
    r = analyze(text, fmt="text")
    assert r.outcome == "voicemail"
    assert r.score < 30


def test_ivr_detected():
    text = """
    Agent: Hello?
    Customer: Thank you for calling. For sales press 1. For support press 2.
    """
    r = analyze(text, fmt="text")
    assert r.outcome == "ivr"


def test_dnc_penalized():
    text = """
    Agent: Hi, this is Leon with Core Dispatch.
    Customer: Take me off your list and do not call again.
    """
    r = analyze(text, fmt="text")
    assert "dnc" in r.events
    assert r.score <= 30


def test_vapi_json_format():
    data = {
        "id": "call_123",
        "messages": [
            {"role": "assistant", "message": "Hi, who's this?"},
            {"role": "user", "message": "This is Dana, not interested thanks."},
        ],
    }
    r = analyze(data, fmt="vapi")
    assert r.call_id == "call_123"
    assert r.outcome == "human_reached"
    assert "objection" in r.events


def test_parse_roundtrip_and_metrics():
    t = parse_transcript("Agent: hello there\nCustomer: hi friend how are you", fmt="text")
    assert len(t.agent_turns) == 1
    assert len(t.customer_turns) == 1
    r = analyze(t.full_text(), fmt="text")
    assert r.metrics["turns"] >= 1



def test_cli_exports_csv_and_jsonl(tmp_path):
    from callscope.cli import main

    transcript = tmp_path / "call_001.txt"
    transcript.write_text(
        "Agent: Hi, can I help?\nCustomer: Yes, how much does it cost?\n",
        encoding="utf-8",
    )
    csv_path = tmp_path / "report.csv"
    jsonl_path = tmp_path / "report.jsonl"

    code = main(["analyze", str(tmp_path), "--csv", str(csv_path), "--jsonl", str(jsonl_path)])

    assert code == 0
    assert "call_id,outcome,score,events" in csv_path.read_text(encoding="utf-8")
    assert "price_discussed" in csv_path.read_text(encoding="utf-8")
    assert jsonl_path.read_text(encoding="utf-8").count("\n") == 1


def _run() -> None:
    fns = sorted(
        (v for k, v in globals().items() if k.startswith("test_") and callable(v)),
        key=lambda f: f.__name__,
    )
    for fn in fns:
        if fn.__name__.endswith("csv_and_jsonl"):
            import tempfile
            from pathlib import Path
            with tempfile.TemporaryDirectory() as d:
                fn(Path(d))
        else:
            fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)}/{len(fns)} passed")


if __name__ == "__main__":
    _run()
