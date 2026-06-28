"""Classify call outcome, detect events, and score conversation quality."""
from __future__ import annotations

import re
from typing import Any, Dict, List

from callscope.models import CallReport, Transcript
from callscope.parser import parse_transcript
from callscope.signals import DEFAULT_PACK, SignalPack, any_match, count_matches

_WORD = re.compile(r"\w+")

# Base score by outcome; detected events adjust from here.
_OUTCOME_BASE = {
    "human_reached": 55,
    "voicemail": 12,
    "ivr": 6,
    "no_answer": 0,
}


def _words(text: str) -> int:
    return len(_WORD.findall(text))


def _classify_outcome(t: Transcript, pack: SignalPack) -> str:
    """Decide what kind of call this was.

    Voicemail and IVR are checked first because some providers transcribe a
    machine greeting onto the ``user`` channel, which would otherwise look
    like a human. We only trust those when there isn't a real back-and-forth.
    """
    cust = t.customer_text()
    full = t.full_text()
    short_exchange = len(t.customer_turns) <= 2

    if any_match(full, pack.voicemail) and (short_exchange or count_matches(cust, pack.voicemail)):
        return "voicemail"
    if any_match(full, pack.ivr) and short_exchange:
        return "ivr"
    if t.customer_turns and _words(cust) >= 2:
        return "human_reached"
    return "no_answer"


def _detect_events(t: Transcript, pack: SignalPack) -> List[str]:
    """Detect notable events, judged from what the customer said."""
    cust = t.customer_text() or t.full_text()
    checks = [
        ("dnc", pack.dnc),
        ("objection", pack.objection),
        ("callback_requested", pack.callback),
        ("appointment_booked", pack.booking),
        ("price_discussed", pack.price),
    ]
    return [name for name, patterns in checks if any_match(cust, patterns)]


def _score(outcome: str, events: List[str], metrics: Dict[str, Any]) -> int:
    score = _OUTCOME_BASE.get(outcome, 0)
    if "appointment_booked" in events:
        score += 30
    if "price_discussed" in events:
        score += 10
    if "callback_requested" in events:
        score += 5
    if "objection" in events:
        score -= 15
    if "dnc" in events:
        score -= 30
    # Reward a genuinely two-sided conversation, but never when the customer
    # pushed back or asked not to be called.
    negative = "dnc" in events or "objection" in events
    ratio = metrics.get("customer_talk_ratio", 0.0)
    if outcome == "human_reached" and not negative and 0.25 <= ratio <= 0.75:
        score += 10
    return max(0, min(100, score))


def analyze_transcript(t: Transcript, pack: SignalPack = DEFAULT_PACK) -> CallReport:
    """Analyze an already-parsed ``Transcript``."""
    agent_words = sum(_words(x.text) for x in t.agent_turns)
    customer_words = sum(_words(x.text) for x in t.customer_turns)
    total = agent_words + customer_words
    metrics: Dict[str, Any] = {
        "turns": len(t.turns),
        "customer_turns": len(t.customer_turns),
        "agent_words": agent_words,
        "customer_words": customer_words,
        "customer_talk_ratio": round(customer_words / total, 3) if total else 0.0,
    }
    outcome = _classify_outcome(t, pack)
    events = _detect_events(t, pack)
    return CallReport(
        call_id=t.call_id,
        outcome=outcome,
        events=events,
        metrics=metrics,
        score=_score(outcome, events, metrics),
        source=t.source,
    )


def analyze(data: Any, fmt: str = "auto", pack: SignalPack = DEFAULT_PACK) -> CallReport:
    """Parse raw transcript input and analyze it in one call."""
    return analyze_transcript(parse_transcript(data, fmt=fmt), pack=pack)
