"""Core data structures for callscope."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

# A turn's speaker, normalized across providers.
Role = str  # "agent" | "customer" | "unknown"


@dataclass
class Turn:
    """A single utterance in a call."""

    role: Role
    text: str


@dataclass
class Transcript:
    """A parsed call transcript, provider-agnostic."""

    turns: List[Turn] = field(default_factory=list)
    call_id: Optional[str] = None
    source: str = "unknown"

    @property
    def agent_turns(self) -> List[Turn]:
        return [t for t in self.turns if t.role == "agent"]

    @property
    def customer_turns(self) -> List[Turn]:
        return [t for t in self.turns if t.role == "customer"]

    def full_text(self) -> str:
        return "\n".join(t.text for t in self.turns)

    def customer_text(self) -> str:
        return "\n".join(t.text for t in self.turns if t.role == "customer")


@dataclass
class CallReport:
    """The analysis result for a single call."""

    call_id: Optional[str]
    outcome: str
    events: List[str]
    metrics: Dict[str, Any]
    score: int
    source: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
