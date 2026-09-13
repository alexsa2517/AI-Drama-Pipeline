from src.ai_acting_director import build_acting_direction, build_acting_prompt


def test_acting_direction_contains_human_performance_cues():
    turn = {
        "turn": 2,
        "speaker": "CHAR-002",
        "dialogue": "ในที่สุดเจ้าก็มาถึง",
        "emotion": "cold amusement",
    }
    direction = build_acting_direction(turn, {"speaker": "CHAR-001"})
    assert "gaze" in direction["eyeline"]
    assert "blink" in direction["blink"].lower()
    assert "professional film actor" in direction["performance"]
    assert "listening-to-thinking" in direction["transition"]


def test_acting_prompt_covers_each_dialogue_turn():
    scene = {
        "dialogue_lines": [
            {"speaker": "A", "dialogue": "คุณมาที่นี่ทำไม", "emotion": "suspicious"},
            {"speaker": "B", "dialogue": "ฉันมาตามหาเธอ", "emotion": "calm"},
        ]
    }
    prompt = build_acting_prompt(scene)
    assert "PROFESSIONAL AI ACTING DIRECTOR" in prompt
    assert "TURN 1" in prompt and "TURN 2" in prompt
    assert "Eyeline:" in prompt
    assert "Blink:" in prompt
    assert "Breath:" in prompt
