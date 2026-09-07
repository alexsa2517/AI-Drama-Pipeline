from src.audio_direction import build_audio_direction


def test_music_is_optional_and_scene_specific():
    scene = {
        "id": "SCENE-001",
        "dialogue_lines": [
            {"speaker": "A", "dialogue": "คุณมาที่นี่ทำไม", "emotion": "tense", "pause_after": 0.4},
        ],
    }
    prompt = build_audio_direction(scene)
    assert "MUSIC = NONE | USE" in prompt
    assert "Music is OPTIONAL" in prompt
    assert "Do not reuse or repeat music" in prompt


def test_silence_and_adaptive_duration_are_explicit():
    scene = {"speaker": "A", "dialogue": "อย่าเข้ามาใกล้", "emotion": "fear"}
    prompt = build_audio_direction(scene)
    assert "Do not add music just to fill silence" in prompt
    assert "does not need to cover the whole scene" in prompt
    assert "adaptive duration" in prompt
    assert "Do NOT generate music here" in prompt


def test_audio_direction_is_music_only_not_sfx_management():
    scene = {"speaker": "A", "dialogue": "เงียบก่อน", "emotion": "quiet"}
    prompt = build_audio_direction(scene)
    assert "SFX" not in prompt
    assert "sound effects" not in prompt.lower()
