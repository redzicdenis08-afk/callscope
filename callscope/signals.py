"""Keyword / regex signal packs used to classify transcripts.

Everything here is intentionally simple and overridable. Build your own
:class:`SignalPack` and pass it to ``analyze`` to tune detection for your
vertical, brand, or language.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Pattern


def _compile(patterns: List[str]) -> List[Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


# Machine-greeting markers. Deliberately specific: the bare word "voicemail"
# is excluded because humans say "they go to voicemail" all the time.
VOICEMAIL = [
    r"\bleave a (?:message|name|brief message)\b",
    r"\bat the (?:tone|beep)\b",
    r"\b(?:after|at) the beep\b",
    r"\brecord your (?:message|name)\b",
    r"\byour call has been forwarded\b",
    r"\bplease leave\b",
    r"\bmailbox (?:is )?(?:full|unavailable)\b",
    r"\bnot available to (?:take|answer) your call\b",
]

IVR = [
    r"\bpress \d\b",
    r"\bpara espa(?:ñ|n)ol\b",
    r"\bfor (?:sales|support|billing|new customers)[,]? press\b",
    r"\bmain menu\b",
    r"\byour call (?:is|may be) (?:important|recorded|monitored)\b",
    r"\blisten carefully(?:,)? as our (?:menu )?options\b",
    r"\bto speak (?:with|to) (?:a representative|an operator)\b",
]

OBJECTION = [
    r"\bnot interested\b",
    r"\bno,? (?:thank you|thanks)\b",
    r"\bwe(?:'re| are) (?:all set|good|not looking|not interested)\b",
    r"\bhow did you get (?:my|this) number\b",
    r"\balready have (?:someone|a (?:service|provider))\b",
]

DNC = [
    r"\bdo not call\b",
    r"\btake (?:me|us) off (?:your|the) (?:list|call list)\b",
    r"\bremove (?:me|us) from\b",
    r"\bstop calling\b",
]

BOOKING = [
    r"\b(?:book|schedule|set up) (?:a|an|the|it|that)\b",
    r"\bappointment\b",
    r"\bwhat time\b",
    r"\b(?:tomorrow|today|monday|tuesday|wednesday|thursday|friday) at\b",
    r"\bsign (?:me|us) up\b",
    r"\blet'?s do it\b",
]

PRICE = [
    r"\bhow much\b",
    r"\b(?:price|pricing|cost|rates?)\b",
    r"\$\s?\d+",
    r"\b(?:per month|monthly|a month)\b",
]

CALLBACK = [
    r"\bcall (?:me|us) back\b",
    r"\bcall back\b",
    r"\b(?:i'?m|we'?re) busy\b",
    r"\bnot a good time\b",
    r"\bcall me (?:later|tomorrow|after|in the)\b",
]


@dataclass
class SignalPack:
    """A bundle of compiled detectors. Override any field to customize."""

    voicemail: List[Pattern] = field(default_factory=lambda: _compile(VOICEMAIL))
    ivr: List[Pattern] = field(default_factory=lambda: _compile(IVR))
    objection: List[Pattern] = field(default_factory=lambda: _compile(OBJECTION))
    dnc: List[Pattern] = field(default_factory=lambda: _compile(DNC))
    booking: List[Pattern] = field(default_factory=lambda: _compile(BOOKING))
    price: List[Pattern] = field(default_factory=lambda: _compile(PRICE))
    callback: List[Pattern] = field(default_factory=lambda: _compile(CALLBACK))


DEFAULT_PACK = SignalPack()


def any_match(text: str, patterns: List[Pattern]) -> bool:
    return any(p.search(text) for p in patterns)


def count_matches(text: str, patterns: List[Pattern]) -> int:
    return sum(1 for p in patterns if p.search(text))
