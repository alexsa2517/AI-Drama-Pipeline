from __future__ import annotations

from typing import Any

from .cinematography_director import build_lighting_bible, build_color_bible, build_cinematography_bible
from .feature_film_cinema import build_feature_film_cinema_prompt
from .feature_film_motion import build_feature_film_motion_prompt
from .ai_acting_director import build_acting_prompt
from .ai_sound_director import build_ai_sound_director
from .timeline import build_dialogue_timeline


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


def _estimate_scene_duration(scene: dict[str, Any]) -> float:
    explicit = scene.get("duration") or scene.get("duration_seconds") or scene.get("length_seconds")
    try:
        if explicit is not None:
            return max(1.0, float(explicit))
    except (TypeError, ValueError):
        pass
    dialogue = build_dialogue_timeline(scene)
    if dialogue:
        return round(max(x["end"] + float(x.get("pause_after", 0.25)) for x in dialogue), 2)
    text = _text(scene, "action", "narration", "description")
    return round(max(3.0, min(12.0, 3.5 + len(text) / 80.0)), 2)


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


def _cut_trigger(scene: dict[str, Any]) -> str:
    text = _text(scene, "reveal", "story_purpose", "conflict", "emotional_beat").lower()
    if any(x in text for x in ("reveal", "discovery", "เฉลย", "เปิดเผย", "ค้นพบ")):
        return "cut at the reveal landing or the first meaningful reaction after it"
    if any(x in text for x in ("conflict", "threat", "danger", "ภัย", "อันตราย")):
        return "cut when attention shifts, threat enters the frame, or a reaction changes the stakes"
    return "cut on a completed thought, meaningful action, reaction, or change of attention"


def build_ai_cinematic_director_prompt(episode: dict, scene: dict, scene_index: int = 0) -> str:
    story = _text(scene, "story_purpose", "story_question", "conflict", "reveal", "payoff")
    action = _text(scene, "action", "movement")
    location = scene.get("location", episode.get("location", "unspecified"))
    duration = _estimate_scene_duration(scene)
    return "\n\n".join([
        AI_CINEMATIC_DIRECTOR_MASTER,
        "SCENE DIRECTING DECISION",
        f"Scene: {scene.get('id', scene_index + 1)}",
        f"Location: {location}",
        f"Estimated scene duration: {duration:.2f}s",
        f"Story purpose: {story or 'not explicitly specified — infer from the scene without inventing facts'}",
        f"Emotion: {_emotion(scene)}",
        f"Action / blocking: {action or 'derive from visible action only'}",
        f"Tension: {_tension(scene):.2f}",
        f"Coverage strategy: {_shot_strategy(scene)}",
        f"Primary cut trigger: {_cut_trigger(scene)}",
        "",
        build_cinematography_bible(scene),
        build_lighting_bible(scene),
        build_color_bible(scene),
        build_feature_film_cinema_prompt(episode, scene),
        build_feature_film_motion_prompt(episode, scene),
        build_acting_prompt(scene),
        build_ai_sound_director(episode, scene, scene_index),
        "",
        "SHOT-BY-SHOT TIMELINE CONTRACT",
        "Create a real chronological shot timeline whose intervals exactly cover the scene duration without gaps or overlaps.",
        "For every shot return: shot number, start time, end time, duration, purpose, subject, shot size, camera angle, lens family, camera position, movement, eyeline, axis/screen direction, lighting emphasis, color emphasis, sound emphasis, cut trigger and continuity lock.",
        "Timing must be driven by dialogue beats, action beats, reaction beats, reveal beats and silence—not by arbitrary equal clip lengths.",
        "Do not force a cut. A shot may hold through multiple dialogue lines when performance and geography benefit from staying present.",
        "When actual TTS duration becomes available, rescale or re-time shot boundaries while preserving the editorial beat order.",
        "For 3D scenes, preserve the established 3D visual language; never convert the scene to live action unless explicitly requested.",
    ])


def build_cinematic_shot_timeline(episode: dict, scene: dict, scene_index: int = 0) -> list[dict[str, Any]]:
    """Build a deterministic timing baseline that can be refined by an AI/provider.

    The baseline uses authoritative dialogue timing when available and allocates visual coverage
    around real dialogue/reaction beats rather than generating arbitrary equal-length shots.
    """
    total = _estimate_scene_duration(scene)
    dialogue = build_dialogue_timeline(scene)
    timeline: list[dict[str, Any]] = []

    if not dialogue:
        hold = round(total, 2)
        return [{
            "shot": 1,
            "start": 0.0,
            "end": hold,
            "duration": hold,
            "size": "wide/medium master",
            "angle": "eye level",
            "lens": "wide-normal",
            "subject": "scene",
            "purpose": "establish geography and follow the meaningful action without unnecessary cutting",
            "movement": "motivated slow push or locked-off hold",
            "cut_reason": "end of scene or meaningful change of attention",
        }]

    # Establishing geography before dialogue. Keep it brief but never remove it when geography matters.
    first_start = max(0.0, min(dialogue[0]["start"], 2.5))
    if first_start > 0.15:
        timeline.append({
            "shot": 1,
            "start": 0.0,
            "end": round(first_start, 2),
            "duration": round(first_start, 2),
            "size": "wide establishing",
            "angle": "eye level",
            "lens": "wide",
            "subject": "scene geography",
            "purpose": "orient the audience before the first spoken beat",
            "movement": "locked-off or restrained establishing movement",
            "cut_reason": "first dialogue/action beat begins",
        })

    shot_no = len(timeline) + 1
    speakers = []
    for turn in dialogue:
        if turn["speaker"] not in speakers:
            speakers.append(turn["speaker"])

    for i, turn in enumerate(dialogue):
        start = float(turn["start"])
        end = float(turn["end"])
        speaker = turn["speaker"]
        timeline.append({
            "shot": shot_no,
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": round(max(0.0, end - start), 2),
            "size": "medium close-up" if len(dialogue) <= 4 else "over-the-shoulder / medium",
            "angle": "eye level",
            "lens": "normal",
            "subject": speaker,
            "purpose": f"deliver turn {turn['turn']} while showing the speaker's intention and performance",
            "movement": "subtle motivated hold or slow push only if emotion escalates",
            "eyeline": "toward listener / correct target",
            "cut_reason": "completed thought or next meaningful reaction",
        })
        shot_no += 1

        pause = float(turn.get("pause_after", 0.25))
        next_start = float(dialogue[i + 1]["start"]) if i + 1 < len(dialogue) else total
        reaction_end = min(next_start, end + pause)
        if reaction_end - end >= 0.12:
            listener = next((x for x in speakers if x != speaker), "listener")
            timeline.append({
                "shot": shot_no,
                "start": round(end, 2),
                "end": round(reaction_end, 2),
                "duration": round(reaction_end - end, 2),
                "size": "reaction close-up" if len(dialogue) <= 4 else "reaction medium close-up",
                "angle": "reverse angle / OTS",
                "lens": "normal-long",
                "subject": listener,
                "purpose": "allow the listener to process the line and reveal emotional consequence",
                "movement": "hold; micro-expression and breathing carry the beat",
                "eyeline": "toward active speaker",
                "cut_reason": "listener response completes or next speaker begins",
            })
            shot_no += 1

    # Ensure the final interval reaches the exact scene end without overlap.
    if timeline:
        timeline[-1]["end"] = round(total, 2)
        timeline[-1]["duration"] = round(max(0.0, total - float(timeline[-1]["start"])), 2)

    return timeline


# Backward-compatible alias used by existing QA/prompt code.
def build_cinematic_shot_plan(episode: dict, scene: dict, scene_index: int = 0) -> list[dict[str, Any]]:
    return build_cinematic_shot_timeline(episode, scene, scene_index)
