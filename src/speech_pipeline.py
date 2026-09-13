from __future__ import annotations

from .animation_rules import build_character_animation_context


def build_speech_spec(episode: dict, scene: dict) -> dict:
    """Build a provider-neutral speech + lip-sync specification for one scene."""
    dialogue = (scene.get("dialogue") or "").strip()
    speaker = (scene.get("speaker") or "").strip()
    return {
        "scene_id": scene["id"],
        "speaker": speaker,
        "dialogue": dialogue,
        "language": episode.get("language", "th"),
        "emotion": scene.get("emotion", "natural"),
        "delivery": scene.get("delivery", "natural conversational delivery"),
        "voice_direction": "Natural human speech, clear Thai pronunciation, realistic breathing and pauses.",
        "lip_sync": "Accurate lip-sync: match phonemes and mouth shapes precisely to the supplied dialogue; no mouth movement when silent.",
        "animation_context": build_character_animation_context(episode, scene),
        "audio_requirements": [
            "clean dialogue",
            "consistent character voice",
            "natural breaths",
            "no music over dialogue",
            "no clipping or robotic artifacts",
        ],
    }


def build_dialogue_video_prompt(episode: dict, scene: dict) -> str:
    spec = build_speech_spec(episode, scene)
    if not spec["dialogue"]:
        return ""
    duration = float(scene.get("duration_seconds", 8))
    return (
        f"Create a cinematic talking-character shot for {duration:g} seconds. "
        f"The speaker is {spec['speaker'] or 'the active character'}. "
        f"The character says exactly: \"{spec['dialogue']}\". "
        f"Emotion: {spec['emotion']}. Delivery: {spec['delivery']}. "
        "Use precise Thai lip-sync, natural jaw/lip/cheek motion, irregular blinking, believable gaze shifts, "
        "subtle breathing and micro-expressions. Keep identity, face, eyes, hair and wardrobe consistent. "
        "Do not add or change dialogue. Do not move the mouth during pauses. "
        "Avoid crossed eyes, pupil jitter, face warping, rubber mouth, frozen stare, or expression resets."
    )
