from __future__ import annotations

from typing import Any

from .dialogue_scene import normalize_dialogue


def build_two_character_timeline(scene: dict) -> list[dict[str, Any]]:
    turns = normalize_dialogue(scene)
    timeline: list[dict[str, Any]] = []
    cursor = 0.0
    for turn in turns:
        seconds = max(1.0, len(turn['dialogue']) / 10.0)
        timeline.append({
            'turn': turn['turn'],
            'speaker': turn['speaker'],
            'start': round(cursor, 2),
            'end': round(cursor + seconds, 2),
            'dialogue': turn['dialogue'],
            'emotion': turn['emotion'],
            'listener': None,
            'pause_after': float(turn.get('pause_after', 0.25)),
        })
        cursor += seconds + float(turn.get('pause_after', 0.25))
    speakers = []
    for item in timeline:
        if item['speaker'] not in speakers:
            speakers.append(item['speaker'])
    if len(speakers) >= 2:
        for item in timeline:
            item['listener'] = next(s for s in speakers if s != item['speaker'])
    return timeline


def build_two_character_prompt(scene: dict) -> str:
    timeline = build_two_character_timeline(scene)
    if not timeline:
        return ''
    location = scene.get('location', '')
    lines = [
        'TWO-CHARACTER CONVERSATION MASTER RULES',
        f'ABSOLUTE LOCATION LOCK: {location}',
        'All dialogue turns happen in ONE continuous physical location.',
        'Camera coverage may change, but never relocate, redesign or replace the environment.',
        'Preserve architecture, furniture, doors, windows, signs, lighting, wardrobe and spatial blocking.',
        'Only the active speaker moves their mouth. The listener remains silent.',
        'The listener must look toward the speaker, blink naturally, breathe, and show subtle emotional reactions.',
        'Maintain screen direction and believable eyelines throughout the conversation.',
        'Never invent dialogue or swap speaker identities.',
        'Actual generated audio duration overrides estimated timing, while turn order remains authoritative.',
        'CONVERSATION TIMELINE:',
    ]
    for item in timeline:
        lines.append(
            f"TURN {item['turn']}: {item['start']:.2f}s-{item['end']:.2f}s | "
            f"SPEAKER={item['speaker']} | LISTENER={item['listener']} | "
            f"TEXT=\"{item['dialogue']}\" | EMOTION={item['emotion']} | "
            f"PAUSE={item['pause_after']:.2f}s"
        )
    return '\n'.join(lines)
