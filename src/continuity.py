from __future__ import annotations


def build_character_context(episode: dict) -> str:
    lines = []
    for c in episode.get("characters", []):
        lines.append(
            f"CHARACTER {c.get('id')}: {c.get('name')}. "
            f"Role: {c.get('role', '')}. Appearance: {c.get('appearance', '')}. "
            f"Personality: {c.get('personality', '')}. "
            f"Continuity: {c.get('continuity_notes', '')}"
        )
    return "\n".join(lines)


def scene_continuity_context(episode: dict, scene_index: int) -> str:
    scenes = episode.get("scenes", [])
    previous = scenes[max(0, scene_index - 2):scene_index]
    if not previous:
        return "No previous scene. Establish the visual baseline."
    return "Previous scene continuity:\n" + "\n".join(
        f"- {s.get('id')}: {s.get('location')} / {s.get('action')}" for s in previous
    )
