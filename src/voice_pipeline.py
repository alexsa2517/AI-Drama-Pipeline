from __future__ import annotations

from pathlib import Path
from typing import Any

from .speech_pipeline import build_speech_spec


def build_voice_manifest(episode: dict, scene: dict, output_dir: str = "outputs/audio") -> dict[str, Any]:
    """Create an executable, provider-neutral manifest for generating one character voice track."""
    spec = build_speech_spec(episode, scene)
    output = Path(output_dir) / f"{scene['id']}.wav"
    return {
        "scene_id": scene["id"],
        "speaker": spec["speaker"],
        "language": spec["language"],
        "dialogue": spec["dialogue"],
        "emotion": spec["emotion"],
        "delivery": spec["delivery"],
        "output_audio": str(output),
        "lip_sync_required": bool(spec["dialogue"]),
        "voice_identity_required": bool(spec["speaker"]),
        "timing_source": "generated_audio_duration",
        "requirements": spec["audio_requirements"],
    }


def build_tts_instruction(manifest: dict[str, Any]) -> str:
    """Return a concise instruction that can be sent to any Thai TTS provider."""
    return (
        f"Generate Thai speech for character {manifest['speaker']}. "
        f"Emotion: {manifest['emotion']}. Delivery: {manifest['delivery']}. "
        f"Speak EXACTLY this text and nothing else: \"{manifest['dialogue']}\". "
        "Use a stable voice identity for this character across all scenes. "
        "Natural breathing and pauses; no music, no SFX, no added words."
    )
