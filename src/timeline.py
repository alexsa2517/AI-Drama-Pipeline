from __future__ import annotations

from typing import Any

from .dialogue_scene import normalize_dialogue


DEFAULT_PAUSE = 0.25


def build_dialogue_timeline(scene: dict) -> list[dict[str, Any]]:
    """Build one authoritative timing track for dialogue, silence and reactions."""
    turns = normalize_dialogue(scene)
    timeline: list[dict[str, Any]] = []
    cursor = 0.0

    for turn in turns:
        text = turn["dialogue"]
        # Conservative speaking estimate for planning only; actual TTS duration wins later.
        speaking_seconds = max(1.0, len(text) / 10.0)
        timeline.append({
            "turn": turn["turn"],
            "speaker": turn["speaker"],
            "start": round(cursor, 2),
            "end": round(cursor + speaking_seconds, 2),
            "dialogue": text,
            "emotion": turn["emotion"],
            "pause_after": turn.get("pause_after", DEFAULT_PAUSE),
        })
        cursor += speaking_seconds + float(turn.get("pause_after", DEFAULT_PAUSE))

    return timeline


def build_timeline_prompt(scene: dict) -> str:
    timeline = build_dialogue_timeline(scene)
    if not timeline:
        return ""

    lines = [
        "AUTHORITATIVE DIALOGUE TIMELINE",
        "Use one continuous scene timeline. Actual generated audio duration overrides estimates, but speaker order and pauses remain authoritative.",
        "During each dialogue interval only the active speaker moves their mouth. During pause intervals all characters remain silent while maintaining natural breathing and reactions.",
    ]
    for item in timeline:
        lines.append(
            f"TURN {item['turn']}: {item['start']:.2f}s–{item['end']:.2f}s | "
            f"SPEAKER={item['speaker']} | DIALOGUE=\"{item['dialogue']}\" | "
            f"EMOTION={item['emotion']} | PAUSE={float(item['pause_after']):.2f}s"
        )
    return "\n".join(lines)
