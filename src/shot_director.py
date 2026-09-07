from __future__ import annotations

from typing import Any

from .dialogue_scene import normalize_dialogue


def build_shot_list(scene: dict) -> list[dict[str, Any]]:
    """Create a restrained shot-by-shot plan while keeping one scene continuous."""
    turns = normalize_dialogue(scene)
    if not turns:
        return [{"shot": 1, "type": "medium shot", "subject": "scene", "purpose": "establish action"}]

    speakers = []
    for t in turns:
        if t["speaker"] not in speakers:
            speakers.append(t["speaker"])

    shots: list[dict[str, Any]] = []
    shots.append({"shot": 1, "type": "wide two-shot", "subject": "all characters", "purpose": "establish spatial relationship"})

    shot_no = 2
    for i, turn in enumerate(turns):
        speaker = turn["speaker"]
        listener = next((s for s in speakers if s != speaker), None)
        camera_type = "medium close-up" if len(turns) <= 4 else "over-the-shoulder"
        shots.append({
            "shot": shot_no,
            "type": camera_type,
            "subject": speaker,
            "purpose": f"speaker turn {turn['turn']}; capture dialogue, gaze and facial performance",
            "dialogue_turn": turn["turn"],
        })
        shot_no += 1
        if listener:
            shots.append({
                "shot": shot_no,
                "type": "reaction close-up",
                "subject": listener,
                "purpose": "listen silently, maintain eye contact, blink naturally and react before responding",
                "dialogue_turn": turn["turn"],
            })
            shot_no += 1

    return shots


def build_shot_director_prompt(scene: dict) -> str:
    shots = build_shot_list(scene)
    lines = [
        "SHOT-BY-SHOT DIRECTOR",
        "Treat this as ONE continuous dramatic scene. Camera coverage may change, but the environment, lighting, wardrobe, identity and character blocking remain continuous.",
        "Cut only at natural conversational beats. Never cut in the middle of a phoneme or create a discontinuity in lip-sync.",
        "The active speaker owns the mouth movement. The listener stays silent and performs believable listening reactions.",
        "Maintain screen direction and eyelines: characters look toward each other, not randomly toward the camera.",
        "Prefer motivated coverage over excessive cuts. Use the two-shot when both characters need to be understood simultaneously.",
    ]
    for shot in shots:
        lines.append(
            f"SHOT {shot['shot']}: {shot['type']} | Subject: {shot['subject']} | Purpose: {shot['purpose']}"
        )
    return "\n".join(lines)
