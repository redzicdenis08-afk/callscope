"""callscope: outcome analytics and quality scoring for AI voice-agent calls."""
from callscope.analyzer import analyze, analyze_transcript
from callscope.models import CallReport, Transcript, Turn
from callscope.parser import parse_transcript
from callscope.signals import DEFAULT_PACK, SignalPack

__version__ = "0.1.0"
__all__ = [
    "analyze",
    "analyze_transcript",
    "parse_transcript",
    "CallReport",
    "Transcript",
    "Turn",
    "SignalPack",
    "DEFAULT_PACK",
]
