from src.timeline import build_dialogue_timeline, build_timeline_prompt


def test_dialogue_timeline_orders_turns():
    scene = {
        "dialogue_lines": [
            {"speaker": "A", "dialogue": "สวัสดี", "pause_after": 0.3},
            {"speaker": "B", "dialogue": "คุณเป็นใคร", "pause_after": 0.5},
        ]
    }
    timeline = build_dialogue_timeline(scene)
    assert len(timeline) == 2
    assert timeline[0]["start"] == 0.0
    assert timeline[1]["start"] > timeline[0]["end"]


def test_timeline_prompt_has_speaker_intervals():
    scene = {"speaker": "A", "dialogue": "ไปกันเถอะ"}
    prompt = build_timeline_prompt(scene)
    assert "AUTHORITATIVE DIALOGUE TIMELINE" in prompt
    assert "SPEAKER=A" in prompt
    assert "PAUSE=" in prompt
