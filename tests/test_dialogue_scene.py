from src.dialogue_scene import build_camera_plan, build_conversation_prompt, normalize_dialogue


def test_multi_turn_conversation_in_one_scene():
    scene = {
        "id": "SC010",
        "dialogue_lines": [
            {"speaker": "CHAR-001", "dialogue": "คุณมาที่นี่ทำไม?", "emotion": "suspicious"},
            {"speaker": "CHAR-002", "dialogue": "ฉันมาตามหาเธอ", "emotion": "calm"},
            {"speaker": "CHAR-001", "dialogue": "แล้วรู้ได้อย่างไรว่าฉันอยู่ที่นี่?", "emotion": "afraid"},
        ],
    }
    turns = normalize_dialogue(scene)
    assert len(turns) == 3
    prompt = build_conversation_prompt(scene)
    assert "same continuous scene" in prompt
    assert "listener remains silent" in prompt
    assert "CHAR-002" in prompt


def test_camera_plan_for_two_speakers():
    scene = {"dialogue_lines": [
        {"speaker": "A", "dialogue": "Hello"},
        {"speaker": "B", "dialogue": "Hi"},
    ]}
    plan = build_camera_plan(scene)
    assert any("two-shot" in shot for shot in plan)
    assert any("over-the-shoulder" in shot for shot in plan)
