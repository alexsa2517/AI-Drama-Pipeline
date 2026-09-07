from src.speech_pipeline import build_dialogue_video_prompt, build_speech_spec


def test_speech_spec_contains_lipsync_and_dialogue():
    episode = {"language": "th"}
    scene = {
        "id": "SC001",
        "duration_seconds": 8,
        "speaker": "CHAR-001",
        "dialogue": "อย่าเข้ามาใกล้!",
        "emotion": "fear",
    }
    spec = build_speech_spec(episode, scene)
    assert spec["dialogue"] == "อย่าเข้ามาใกล้!"
    assert "lip-sync" in spec["lip_sync"].lower()
    assert "blinking" in spec["animation_context"].lower()


def test_talking_video_prompt_is_explicit():
    episode = {"language": "th"}
    scene = {
        "id": "SC001",
        "duration_seconds": 8,
        "speaker": "CHAR-001",
        "dialogue": "ฉันได้ยินเสียงอะไรบางอย่าง",
    }
    prompt = build_dialogue_video_prompt(episode, scene)
    assert "says exactly" in prompt
    assert "Thai lip-sync" in prompt
    assert "natural jaw" in prompt
    assert "gaze shifts" in prompt
