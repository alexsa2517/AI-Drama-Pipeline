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


def build_scene_visual_lock(scene: dict) -> str:
    """Hard-lock the current scene's environment so generation cannot casually relocate it."""
    location = scene.get("location", "")
    time = scene.get("time", "")
    action = scene.get("action", "")
    return "\n".join([
        "HARD SCENE VISUAL LOCK",
        f"EXACT LOCATION: {location}",
        f"EXACT TIME/CONDITIONS: {time}",
        f"SCENE ACTION: {action}",
        "The exact location above is authoritative. Do NOT replace, reinterpret or relocate the scene to another setting.",
        "If the location is a company/office/building, it must remain that same company/office/building throughout the scene.",
        "Do not turn an office into a street, home, warehouse, cafe, outdoor area or generic room unless the scene explicitly says so.",
        "Camera angle changes are allowed, but camera changes must reveal different views of the SAME physical environment.",
        "Preserve fixed environmental landmarks, architecture, furniture, doors, windows, signage and spatial layout whenever they are established.",
        "Character movement may change position inside the environment, but must not change the environment itself.",
    ])


def scene_continuity_context(episode: dict, scene_index: int) -> str:
    scenes = episode.get("scenes", [])
    current = scenes[scene_index] if 0 <= scene_index < len(scenes) else {}
    previous = scenes[max(0, scene_index - 2):scene_index]
    current_location = current.get("location", "")
    lines = [
        "SCENE CONTINUITY CONTROL",
        f"CURRENT SCENE LOCATION (AUTHORITATIVE): {current_location}",
        "The current scene location takes priority over all previous-scene locations.",
        "Previous scenes are continuity references only; NEVER copy a previous location into the current scene unless the current scene explicitly uses the same location.",
    ]
    if not previous:
        lines.append("No previous scene. Establish the current scene as the visual baseline.")
    else:
        lines.append("Previous scene continuity references:")
        lines.extend(
            f"- {s.get('id')}: {s.get('location')} / {s.get('action')}" for s in previous
        )
    return "\n".join(lines)
