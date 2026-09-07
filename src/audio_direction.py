from __future__ import annotations

from .timeline import build_dialogue_timeline


def build_audio_direction(scene: dict) -> str:
    """Create adaptive background-music direction; music is optional and scene-specific."""
    timeline = build_dialogue_timeline(scene)

    lines = [
        "ADAPTIVE BACKGROUND MUSIC DECISION",
        "Decide independently for this scene whether background music improves the story.",
        "Music is OPTIONAL. NONE is a valid and often preferable decision.",
        "Do not reuse or repeat music merely because the previous scene used music.",
        "Judge the decision from the scene's situation, emotion, tension, pacing, dialogue and visual action.",
        "Do not add music just to fill silence. Silence is an intentional dramatic choice.",
        "If music is NOT needed, explicitly choose MUSIC=NONE and preserve clean silence.",
        "If music IS needed, choose an appropriate mood/style for THIS scene rather than a fixed series-wide track.",
        "Choose adaptively when the music should enter, leave, fade, pause or stop; it does not need to cover the whole scene.",
        "Music duration must follow the dramatic beat, not a fixed duration or template.",
        "During important dialogue, keep music subtle and below speech; reduce or remove it when silence gives the moment more impact.",
        "A scene may start with music, end with silence, contain only a short musical cue, or contain no music at all.",
        "Do NOT generate music here. Produce only a direction/specification for the production pipeline.",
    ]

    if timeline:
        lines.append("DIALOGUE BEATS FOR MUSIC DECISION")
        for item in timeline:
            lines.append(
                f"TURN {item['turn']} ({item['speaker']}): "
                f"{item['start']:.2f}s–{item['end']:.2f}s; "
                f"emotion={item['emotion']}; pause_after={float(item['pause_after']):.2f}s. "
                "Re-evaluate whether music should continue, fade, pause or stop around this beat."
            )

    lines.extend([
        "OUTPUT DECISION:",
        "MUSIC = NONE | USE",
        "If USE: specify scene-appropriate mood/style, approximate entry, approximate exit, adaptive duration and intensity.",
        "Never force the same music choice across scenes unless the story context genuinely calls for continuity.",
    ])
    return "\n".join(lines)
