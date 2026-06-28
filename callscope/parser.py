"""Parse call transcripts from common voice-AI formats into a ``Transcript``."""
from __future__ import annotations

import json
from typing import Any, List, Optional

from callscope.models import Transcript, Turn

_AGENT_ROLES = {"agent", "assistant", "bot", "ai", "system"}
_CUSTOMER_ROLES = {"customer", "user", "human", "caller", "lead", "prospect"}

_AGENT_PREFIXES = ("agent:", "assistant:", "bot:", "ai:", "rep:", "leon:")
_CUSTOMER_PREFIXES = ("customer:", "user:", "human:", "caller:", "lead:", "prospect:")


def _norm_role(raw: str) -> str:
    r = (raw or "").strip().lower()
    if r in _AGENT_ROLES:
        return "agent"
    if r in _CUSTOMER_ROLES:
        return "customer"
    return "unknown"


def parse_vapi(data: Any) -> Transcript:
    """Parse a VAPI-style call object or a list of message dicts."""
    call_id: Optional[str] = None
    messages: Any = data
    if isinstance(data, dict):
        call_id = data.get("id") or data.get("callId")
        messages = (
            data.get("messages")
            or data.get("transcript")
            or data.get("turns")
            or []
        )
    if isinstance(messages, str):
        return parse_text(messages, call_id=call_id, source="vapi")

    turns: List[Turn] = []
    for m in messages or []:
        if not isinstance(m, dict):
            continue
        role = _norm_role(m.get("role", ""))
        text = (m.get("message") or m.get("text") or m.get("content") or "").strip()
        if text:
            turns.append(Turn(role=role, text=text))
    return Transcript(turns=turns, call_id=call_id, source="vapi")


def parse_text(raw: str, call_id: Optional[str] = None, source: str = "text") -> Transcript:
    """Parse a plain-text transcript with optional ``Speaker: text`` prefixes."""
    turns: List[Turn] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        low = line.lower()
        role, text = "unknown", line
        matched = False
        for p in _AGENT_PREFIXES:
            if low.startswith(p):
                role, text, matched = "agent", line[len(p):].strip(), True
                break
        if not matched:
            for p in _CUSTOMER_PREFIXES:
                if low.startswith(p):
                    role, text = "customer", line[len(p):].strip()
                    break
        if text:
            turns.append(Turn(role=role, text=text))
    return Transcript(turns=turns, call_id=call_id, source=source)


def parse_transcript(data: Any, fmt: str = "auto") -> Transcript:
    """Dispatch to the right parser. ``fmt`` is ``auto`` | ``vapi`` | ``text``."""
    if fmt == "text":
        return parse_text(data if isinstance(data, str) else str(data))
    if fmt == "vapi":
        if isinstance(data, str):
            data = json.loads(data)
        return parse_vapi(data)

    # auto-detect
    if isinstance(data, (dict, list)):
        return parse_vapi(data)
    if isinstance(data, str):
        s = data.strip()
        if s[:1] in ("{", "["):
            try:
                return parse_vapi(json.loads(s))
            except json.JSONDecodeError:
                pass
        return parse_text(data)
    raise TypeError(f"Unsupported transcript input type: {type(data)!r}")
