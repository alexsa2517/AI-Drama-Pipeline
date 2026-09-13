from __future__ import annotations

from typing import Any


DEFAULT_CAMERA_SEQUENCE = [
    "wide establishing two-shot",
    "medium two-shot",
    "over-the-shoulder on speaker A",
    "over-the-shoulder on speaker B",
    "close-up on the active speaker",
    "reaction close-up",
]


def normalize_dialogue(scene: dict) -> list[dict[str, Any]]:
    """Normalize one scene's dialogue into ordered conversational turns.

    Supports the existing single `speaker`/`dialogue` fields and the richer
    `dialogue_lines` list without breaking older episode YAML files.
    """
    lines = scene.get("dialogue_lines")
    if isinstance(lines, list) and lines:
        turns = []
        for i, line in enumerate(lines, 1):
            if not isinstance(line, dict):
                continue
            text = str(line.get("dialogue", "")).strip()
            speaker = str(line.get("speaker", "")).strip()
            if text and speaker:
                turns.append({
                    "turn": i,
                    "speaker": speaker,
                    "dialogue": text,
                    "emotion": line.get("emotion", scene.get("emotion", "natural")),
                    "delivery": line.get("delivery", scene.get("delivery", "natural conversational delivery")),
                    "pause_after": float(line.get("pause_after", 0.25)),
                    "acting_notes": line.get("acting_notes", ""),
                })
        return turns

    text = str(scene.get("dialogue", "")).strip()
    speaker = str(scene.get("speaker", "")).strip()
    if text and speaker:
        return [{
            "turn": 1,
            "speaker": speaker,
            "dialogue": text,
            "emotion": scene.get("emotion", "natural"),
            "delivery": scene.get("delivery", "natural conversational delivery"),
            "pause_after": 0.25,
            "acting_notes": scene.get("acting_notes", ""),
        }]
    return []


def build_conversation_prompt(scene: dict) -> str:
    """Create a single-shot conversational direction for a video model."""
    turns = normalize_dialogue(scene)
    if not turns:
        return ""

    lines = [
        "CONVERSATIONAL SCENE — keep all dialogue turns inside the same continuous scene.",
        "The characters must listen to each other and respond in sequence, never talking over each other unless explicitly requested.",
        "Preserve the same room, lighting, wardrobe, character identity and spatial positions throughout the scene.",
        "Use motivated camera changes within the same scene; do not teleport characters or reset the environment.",
        "Dialogue timing is authoritative: mouth movement follows the active speaker only; the listener remains silent and reacts naturally.",
        "Natural eye contact is directional, not a frozen stare. The listener looks at the speaker, briefly looks away, blinks naturally, then returns attention.",
    ]
    for turn in turns:
        lines.append(
            f"TURN {turn['turn']} — {turn['speaker']}: \"{turn['dialogue']}\" "
            f"Emotion: {turn['emotion']}. Delivery: {turn['delivery']}. "
            f"Pause after: {turn['pause_after']:.2f}s."
        )
    return "\n".join(lines)


def build_camera_plan(scene: dict) -> list[str]:
    """Select a restrained camera sequence for a multi-character conversation."""
    turns = normalize_dialogue(scene)
    speakers = []
    for turn in turns:
        if turn["speaker"] not in speakers:
            speakers.append(turn["speaker"])

    if len(speakers) <= 1:
        return ["medium shot", "subtle push-in", "close-up reaction"]

    plan = DEFAULT_CAMERA_SEQUENCE.copy()
    # More turns need fewer camera cuts so the conversation remains coherent.
    if len(turns) >= 5:
        plan = ["medium two-shot", "over-the-shoulder on active speaker", "reaction close-up"]
    return plan
