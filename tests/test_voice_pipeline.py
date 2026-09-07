from src.voice_pipeline import build_tts_instruction, build_voice_manifest


def test_voice_manifest_binds_dialogue_to_character():
    episode = {"language": "th"}
    scene = {
        "id": "SC001",
        "speaker": "CHAR-001",
        "dialogue": "คุณมาที่นี่ทำไม",
        "emotion": "suspicious",
        "delivery": "quiet and controlled",
    }
    manifest = build_voice_manifest(episode, scene)
    assert manifest["speaker"] == "CHAR-001"
    assert manifest["dialogue"] == "คุณมาที่นี่ทำไม"
    assert manifest["language"] == "th"
    assert manifest["lip_sync_required"] is True
    assert manifest["voice_identity_required"] is True
    assert manifest["timing_source"] == "generated_audio_duration"


def test_tts_instruction_forbids_added_words():
    manifest = {
        "speaker": "CHAR-001",
        "dialogue": "อย่าเข้ามาใกล้",
        "emotion": "fear",
        "delivery": "whispered",
    }
    prompt = build_tts_instruction(manifest)
    assert "EXACTLY this text and nothing else" in prompt
    assert "no music, no SFX" in prompt
