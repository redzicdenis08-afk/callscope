import json
from callscope import analyze

def test_callback_booking_mix():
    data = {
        "id": "call_mixed_001",
        "messages": [
            {"role": "assistant", "message": "Hi this is Leon with Core Dispatch, how's it going?"},
            {"role": "user", "message": "Hey Leon, I am a bit busy right now. Can you call me back at 3 PM? Also, how much does it cost?"},
            {"role": "assistant", "message": "Sure, it is 149 a month. I'll book that callback for 3 PM."},
            {"role": "user", "message": "Sounds perfect, let's book it."}
        ]
    }
    r = analyze(data, fmt="vapi")
    assert r.outcome == "human_reached"
    assert "price_discussed" in r.events
    assert "callback_requested" in r.events
    assert r.score >= 70
