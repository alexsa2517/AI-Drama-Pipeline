from __future__ import annotations

from typing import Any


def generate_story_seed(
    premise: str,
    title: str = "Untitled Episode",
    genre: str = "dark fantasy",
    language: str = "th",
) -> dict[str, Any]:
    """Create a deterministic story structure without an external LLM/API.

    This is intentionally template-based in V1.2 so the pipeline remains
    testable and provider-agnostic before any model is allowed to generate
    production content.
    """
    premise = premise.strip()
    if not premise:
        raise ValueError("premise must not be empty")

    return {
        "id": "EP-AUTO-001",
        "title": title.strip() or "Untitled Episode",
        "logline": premise,
        "genre": genre,
        "language": language,
        "characters": [
            {
                "id": "CHAR-001",
                "name": "The Protagonist",
                "role": "protagonist",
                "appearance": "consistent facial features, hairstyle, costume, and silhouette across every scene",
                "personality": "curious, cautious, determined",
                "continuity_notes": "Keep identity, costume, age, proportions, and key props consistent.",
            }
        ],
        "scenes": [
            {
                "id": "SC001",
                "title": "The Hook",
                "location": "forbidden location",
                "time": "night",
                "action": f"The protagonist encounters the first unsettling sign: {premise}",
                "narration": "เสียงกระซิบจากความมืดเรียกชื่อของเขา... แต่ไม่มีใครอยู่ตรงนั้น",
                "duration_seconds": 8,
            },
            {
                "id": "SC002",
                "title": "The Discovery",
                "location": "deeper inside the forbidden location",
                "time": "night",
                "action": "The protagonist follows the clue and discovers that the danger is closer than expected.",
                "narration": "ยิ่งเดินเข้าไป ความจริงที่ไม่ควรถูกค้นพบก็ยิ่งชัดเจนขึ้น",
                "duration_seconds": 8,
            },
            {
                "id": "SC003",
                "title": "The Cliffhanger",
                "location": "the hidden chamber",
                "time": "night",
                "action": "A hidden presence reveals itself, ending the episode at the moment of greatest uncertainty.",
                "narration": "เมื่อเขาหันกลับมา... สิ่งที่ยืนอยู่ข้างหลังไม่ใช่มนุษย์",
                "duration_seconds": 8,
            },
        ],
    }
