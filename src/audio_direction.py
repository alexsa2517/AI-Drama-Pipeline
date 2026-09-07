from __future__ import annotations

from .timeline import build_dialogue_timeline


def build_audio_direction(scene: dict) -> str:
    """Let the production model choose music/SFX length and intensity from dramatic context."""
    timeline = build_dialogue_timeline(scene)
    if not timeline:
        return "AUDIO DIRECTION\nChoose atmospheric music and sound effects appropriate to the scene; use only what improves the story."

    lines = [
        "ADAPTIVE AUDIO DIRECTION",
        "AI chooses music, ambience and sound-effect timing according to the scene's emotion, pacing and visual action.",
        "Do not force music to run for the entire scene. Start, stop, fade, shorten or extend tracks when the story requires it.",
        "Dialogue has priority over music and effects. Never mask words, breaths or important reactions.",
        "Use silence deliberately before reveals, threats, emotional turns and punchlines when it increases impact.",
        "Music may continue underneath a dialogue exchange only when it remains subtle and does not compete with speech.",
        "Choose SFX only when motivated by visible or implied action; avoid filling every pause with noise.",
        "Prefer clean transitions: short fade-in/out or natural tails rather than abrupt cuts unless a dramatic cut is intentional.",
    ]
    for item in timeline:
        lines.append(
            f"TURN {item['turn']} ({item['speaker']}): dialogue {item['start']:.2f}s–{item['end']:.2f}s; "
            f"pause {float(item['pause_after']):.2f}s; emotion={item['emotion']}. "
            "Adjust music/SFX around this beat as needed."
        )
    return "\n".join(lines)
