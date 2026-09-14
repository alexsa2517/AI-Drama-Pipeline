from __future__ import annotations

from typing import Any

from .cinematography_director import build_lighting_bible, build_color_bible, build_cinematography_bible
from .feature_film_cinema import build_feature_film_cinema_prompt
from .feature_film_motion import build_feature_film_motion_prompt
from .ai_acting_director import build_acting_prompt
from .ai_sound_director import build_ai_sound_director


AI_CINEMATIC_DIRECTOR_MASTER = """AI CINEMATIC DIRECTOR — UNIFIED FILM LANGUAGE

Act as the visual director for a continuous feature-film sequence. Do not choose shots, light, color or camera movement independently. Every visual decision must serve story, performance, motion and sound.

DIRECTING ORDER
1. Story purpose and dramatic question
2. Character objective, emotion and reaction
3. Blocking and natural movement
4. Spatial geography, eyelines and screen direction
5. Shot size, lens, camera position and movement
6. Lighting and color
7. Sound relationship
8. Editorial cut or hold decision

SHOT COVERAGE
Use the minimum coverage needed to tell the scene clearly. Establish geography first when needed, then move to medium interaction, close emotional pressure, reaction, insert or POV only when dramatically justified. Never alternate angles mechanically.

ANGLE LOGIC
- Eye level: neutral human observation.
- Low angle: power, vulnerability from below, scale or threat when motivated.
- High angle: vulnerability, isolation, geography or loss of control when motivated.
- Over-the-shoulder: relationship and eyeline continuity.
- Profile: emotional distance, contemplation or visual geometry.
- POV: subjective discovery or threat; use sparingly.
- Two-shot: preserve relationship when both performances matter.

LENS LOGIC
Wider lenses establish geography and relationships. Normal lenses preserve natural perspective. Longer lenses compress space and isolate emotional pressure. Lens choice must remain coherent within the scene and must not change randomly between cuts.

CAMERA MOVEMENT
Locked-off when observation is strongest. Slow push-in for increasing attention or realization. Lateral/tracking movement for purposeful following or relational change. Handheld only when instability is motivated. Crane/dolly only when spatial or emotional transition justifies it. No random AI camera motion.

CUTTING / ANGLE CHANGES
Cut on thought, reaction, action, reveal, completed speech beat or meaningful change in attention. Do not cut merely because a generated clip ended. Preserve the 180-degree axis, eyelines, screen direction, horizon and spatial geography. Hold on important reactions when the audience needs to process them.

LIGHTING
Use motivated sources and maintain key direction, shadow direction, color temperature, exposure and facial readability across coverage. Light changes must be story-motivated.

COLOR
Maintain one coherent palette across the scene. Emotional grade may evolve gradually with tension, discovery or climax. Protect skin tone and character identity.

SOUND RELATIONSHIP
Camera and edit decisions must leave room for dialogue, foley, ambience, SFX and score. Silence can motivate a hold or cut. Do not use visual intensity to compete with an important line.

AI ARTIFACT SUPPRESSION
No identity drift, pose reset, impossible perspective, floating camera, changing light direction, random lens changes, eyeline mismatch, jumpy blocking, duplicate characters, warped props, flickering exposure or discontinuous color.
"""


def _text(scene: dict[str, Any], *keys: str) -> str:
    return " ".join(str(scene.get(k, "")) for k in keys if scene.get(k)).strip()


def _emotion(scene: dict[str, Any]) -> str:
    return str(scene.get("emotion") or scene.get("emotional_beat") or "natural").strip()


def _tension(scene: dict[str, Any]) -> float:
    value = scene.get("tension", scene.get("tension_level", 0.4))
    try:
        value = float(value)
        return max(0.0, min(1.0, value / 100 if value > 1 else value))
    except (TypeError, ValueError):
        return 0.4


def _shot_strategy(scene: dict[str, Any]) -> str:
    text = _text(scene, "story_purpose", "conflict", "reveal", "action", "payoff").lower()
    tension = _tension(scene)
    if any(x in text for x in ("climax", "final", "payoff", "เฉลย", "ไคลแมกซ์", "จุดพีค")):
        return "Begin with readable geography, compress toward closer emotional coverage, then hold the decisive reaction/reveal before the release."
    if any(x in text for x in ("reveal", "discovery", "mystery", "ค้นพบ", "ความลับ", "เปิดเผย")):
        return "Favor observation and controlled push-in; delay the close-up until the discovery lands. Use reaction coverage after the reveal."
    if tension >= 0.7:
        return "Restrained coverage with shorter motivated changes in angle; protect eyelines and let movement create tension rather than frantic cutting."
    return "Use a stable master/two-shot or establishing frame, then medium/close coverage only when performance or story information requires it."


def build_ai_cinematic_director_prompt(episode: dict, scene: dict, scene_index: int = 0) -> str:
    story = _text(scene, "story_purpose", "story_question", "conflict", "reveal", "payoff")
    action = _text(scene, "action", "movement")
    location = scene.get("location", episode.get("location", "unspecified"))
    return "\n\n".join([
        AI_CINEMATIC_DIRECTOR_MASTER,
        "SCENE DIRECTING DECISION",
        f"Scene: {scene.get('id', scene_index + 1)}",
        f"Location: {location}",
        f"Story purpose: {story or 'not explicitly specified — infer from the scene without inventing facts'}",
        f"Emotion: {_emotion(scene)}",
        f"Action / blocking: {action or 'derive from visible action only'}",
        f"Tension: {_tension(scene):.2f}",
        f"Coverage strategy: {_shot_strategy(scene)}",
        "",
        build_cinematography_bible(scene),
        build_lighting_bible(scene),
        build_color_bible(scene),
        build_feature_film_cinema_prompt(episode, scene),
        build_feature_film_motion_prompt(episode, scene),
        build_acting_prompt(scene),
        build_ai_sound_director(episode, scene, scene_index),
        "",
        "OUTPUT — CINEMATIC SHOT PLAN",
        "For each shot, return: shot number, purpose, subject, shot size, camera angle, lens family, camera position, movement, duration, eyeline, lighting emphasis, color emphasis, sound emphasis, cut reason, and continuity constraint.",
        "The plan must explain WHY the camera changes. If no change is needed, hold the shot.",
    ])


def build_cinematic_shot_plan(episode: dict, scene: dict, scene_index: int = 0) -> list[dict[str, Any]]:
    """Deterministic baseline coverage; AI/provider can refine it without replacing existing shot logic."""
    dialogue = scene.get("dialogue_lines", []) or scene.get("dialogue", [])
    shots: list[dict[str, Any]] = [
        {"shot": 1, "size": "wide/medium master", "angle": "eye level", "lens": "wide-normal", "purpose": "establish geography and blocking", "cut_reason": "scene entry"}
    ]
    if dialogue:
        for index, line in enumerate(dialogue, start=2):
            speaker = line.get("speaker", "active character") if isinstance(line, dict) else "active character"
            shots.append({"shot": index, "size": "medium close-up", "angle": "eye level", "lens": "normal", "subject": speaker, "purpose": "capture performance and dialogue", "cut_reason": "speaker thought/line beat"})
            shots.append({"shot": index + len(dialogue), "size": "reaction close-up", "angle": "eye level", "lens": "normal-long", "subject": "listener", "purpose": "capture processing and emotional reaction", "cut_reason": "reaction changes meaning"})
    else:
        shots.append({"shot": 2, "size": "medium", "angle": "eye level", "lens": "normal", "purpose": "follow meaningful action", "cut_reason": "attention changes"})
    return shots
