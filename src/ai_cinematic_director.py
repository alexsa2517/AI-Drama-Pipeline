from __future__ import annotations

from typing import Any

from .cinematography_director import build_lighting_bible, build_color_bible, build_cinematography_bible
from .feature_film_cinema import build_feature_film_cinema_prompt
from .feature_film_motion import build_feature_film_motion_prompt
from .ai_acting_director import build_acting_prompt
from .ai_sound_director import build_ai_sound_director
from .timeline import build_dialogue_timeline


AI_CINEMATIC_DIRECTOR_MASTER = """AI CINEMATIC DIRECTOR — FEATURE FILM DIRECTING ENGINE

Act as the lead visual director of a continuous feature-film sequence. You are not a shot-list generator. You make editorial decisions: what the audience should see, when they should see it, when NOT to cut, how performance controls framing, and how each scene inherits the physical and emotional state of the previous scene.

DIRECTING PRIORITY
1. Story purpose and dramatic question
2. Character objective, emotion and reaction
3. Blocking, eyelines and natural movement
4. Spatial geography, axis and screen direction
5. Shot size, lens, camera position and movement
6. Lighting and color continuity
7. Sound relationship
8. Editorial cut, hold, reveal and silence decisions

DIRECTOR'S GOLDEN RULES
- Every shot must have a dramatic reason.
- Use the minimum coverage needed. Do not create cuts just to look cinematic.
- If performance is stronger in one uninterrupted shot, HOLD.
- If the audience needs to understand a spatial change, CUT or MOVE with purpose.
- Reaction is often more important than dialogue coverage.
- Silence is an editorial tool, not empty time.
- Camera movement must be motivated by character, discovery, threat, geography or emotional transition.
- Never trade story clarity for visual complexity.

SHOT COVERAGE
Establish geography only as much as needed, then protect the strongest performance. Use master/two-shot, medium, OTS, close-up, insert and POV only when their narrative function is clear. Avoid mechanical shot-reverse-shot patterns.

ANGLE / LENS LOGIC
Eye level is neutral human observation. Low/high angles are motivated by power, vulnerability, scale or geography. OTS protects relationship and eyeline. Profile supports distance or contemplation. POV is subjective and should be earned. Wide lenses establish space; normal lenses preserve natural perspective; longer lenses isolate or compress emotional pressure. Lens changes must be motivated and coherent.

CAMERA MOVEMENT
Locked-off when observation is strongest. Slow push for attention or realization. Tracking/lateral movement for purposeful following or relational change. Handheld only for motivated instability. Dolly/crane only when spatial or emotional transition warrants it. No random AI camera motion.

EDITORIAL DECISION
Cut on thought, reaction, action, reveal, completed speech beat or meaningful change of attention. Hold when the audience should remain inside the performance. Do not cut because a generated clip ended. Do not force a reaction close-up if the listener's reaction is already readable in a two-shot.

LIGHT / COLOR
Use motivated sources. Maintain key direction, shadow direction, exposure, color temperature and facial readability across coverage. Maintain one coherent palette; allow gradual emotional evolution only when story warrants it. Protect skin tone and identity.

SOUND RELATIONSHIP
Visual intensity must not compete with important dialogue, Foley, ambience, SFX or score. A sound cue, silence or off-screen event may be the reason to hold or cut.

CONTINUITY / MEMORY
Treat the end of the previous scene as the starting state of the next scene. Preserve character position, facing direction, eyeline, screen direction, dominant light direction, emotional state, important props, wardrobe state and unresolved action. Never reset characters merely because a new scene begins.

AI ARTIFACT SUPPRESSION
No identity drift, pose reset, impossible perspective, floating camera, random lens changes, eyeline mismatch, jumpy blocking, duplicate characters, warped props, flickering exposure, discontinuous color, temporal texture crawl or unexplained extras.
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
        return "Begin with readable geography, compress toward closer emotional coverage, then hold the decisive reaction/reveal before release."
    if any(x in text for x in ("reveal", "discovery", "mystery", "ค้นพบ", "ความลับ", "เปิดเผย")):
        return "Favor observation and controlled push-in; delay the close-up until discovery lands, then protect the reaction."
    if tension >= 0.7:
        return "Use restrained coverage with shorter motivated changes; let blocking and attention shifts create tension instead of frantic cutting."
    return "Use a stable master/two-shot or establishing frame, then medium/close coverage only when performance or story information requires it."


def _cut_trigger(scene: dict[str, Any]) -> str:
    text = _text(scene, "reveal", "story_purpose", "conflict", "emotional_beat").lower()
    if any(x in text for x in ("reveal", "discovery", "เฉลย", "เปิดเผย", "ค้นพบ")):
        return "cut at the reveal landing or the first meaningful reaction after it"
    if any(x in text for x in ("conflict", "threat", "danger", "ภัย", "อันตราย")):
        return "cut when attention shifts, threat enters the frame, or a reaction changes the stakes"
    return "cut on a completed thought, meaningful action, reaction, or change of attention"


def _scene_state(scene: dict[str, Any]) -> dict[str, str]:
    return {
        "location": str(scene.get("location", "")),
        "characters": str(scene.get("characters", "")),
        "facing": str(scene.get("facing_direction", scene.get("screen_direction", ""))),
        "eyeline": str(scene.get("eyeline", "")),
        "blocking": str(scene.get("blocking", scene.get("movement", ""))),
        "light": str(scene.get("lighting", scene.get("light_direction", ""))),
        "emotion": _emotion(scene),
        "props": str(scene.get("props", scene.get("important_props", ""))),
        "wardrobe": str(scene.get("wardrobe_state", scene.get("wardrobe", ""))),
        "unresolved": str(scene.get("unresolved_action", scene.get("cliffhanger", ""))),
    }


def build_director_scene_memory(episode: dict, scene_index: int = 0) -> str:
    """Create a continuity handoff from the previous scene into the current scene."""
    scenes = episode.get("scenes", [])
    if scene_index <= 0 or scene_index >= len(scenes):
        return "DIRECTOR MEMORY: This is the opening scene. Establish geography, screen direction and visual grammar for later scenes."
    previous = _scene_state(scenes[scene_index - 1])
    current = _scene_state(scenes[scene_index])
    return "\n".join([
        "DIRECTOR MEMORY / SCENE-TO-SCENE HANDOFF",
        f"Previous location: {previous['location'] or 'unspecified'}",
        f"Previous characters: {previous['characters'] or 'unspecified'}",
        f"Previous facing/screen direction: {previous['facing'] or 'preserve from visual continuity'}",
        f"Previous eyeline: {previous['eyeline'] or 'preserve from visual continuity'}",
        f"Previous blocking: {previous['blocking'] or 'preserve the last visible state'}",
        f"Previous light: {previous['light'] or 'preserve motivated direction where physically continuous'}",
        f"Previous emotional state: {previous['emotion']}",
        f"Previous props: {previous['props'] or 'none specified'}",
        f"Previous wardrobe state: {previous['wardrobe'] or 'preserve established state'}",
        f"Previous unresolved action: {previous['unresolved'] or 'none specified'}",
        f"Current location: {current['location'] or 'unspecified'}",
        f"Current emotional state: {current['emotion']}",
        "HANDOFF RULE: Continue from the last visible physical/emotional state. If the location changes, motivate the transition rather than silently resetting geography. If a value is not explicitly known, preserve the established visual lock instead of inventing a contradictory state.",
    ])


def build_director_decision_prompt(episode: dict, scene: dict, scene_index: int = 0, qa_feedback: str = "") -> str:
    """Prompt for a second-pass director review after shot planning or generation QA."""
    return "\n\n".join([
        "DIRECTOR DECISION PASS — REVIEW BEFORE FINAL RENDER",
        "Review the current scene as a film director, not as a prompt formatter.",
        "Ask: What is the audience supposed to notice? What should remain unseen? Which performance beat is strongest? Is every cut necessary? Is the camera movement motivated? Does the scene inherit the previous state?",
        "DECISION OUTPUT",
        "1. KEEP — shots that already serve the story and performance.",
        "2. CHANGE — shots whose size, angle, lens, movement, timing or eyeline weakens the scene.",
        "3. REMOVE — unnecessary coverage, camera movement, music emphasis or cuts.",
        "4. HOLD — moments that should remain uninterrupted for emotional processing.",
        "5. CONTINUITY REPAIR — exact state that must be preserved from the previous scene.",
        "6. FINAL CUT ORDER — concise chronological order of the surviving shots.",
        "Never add complexity merely to make the scene look cinematic.",
        build_director_scene_memory(episode, scene_index),
        f"Current scene: {scene.get('id', scene_index + 1)}",
        f"Story purpose: {_text(scene, 'story_purpose', 'story_question', 'conflict', 'reveal', 'payoff') or 'infer without inventing facts'}",
        f"Emotion: {_emotion(scene)}",
        f"QA feedback: {qa_feedback or 'none provided'}",
    ])


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
        build_director_scene_memory(episode, scene_index),
        build_cinematography_bible(scene),
        build_lighting_bible(scene),
        build_color_bible(scene),
        build_feature_film_cinema_prompt(episode, scene),
        build_feature_film_motion_prompt(episode, scene),
        build_acting_prompt(scene),
        build_ai_sound_director(episode, scene, scene_index),
        "SHOT-BY-SHOT TIMELINE CONTRACT",
        "Create a real chronological shot timeline whose intervals exactly cover the scene duration without gaps or overlaps.",
        "For every shot return: shot number, start time, end time, duration, purpose, subject, shot size, camera angle, lens family, camera position, movement, eyeline, axis/screen direction, lighting emphasis, color emphasis, sound emphasis, cut trigger and continuity lock.",
        "Timing must be driven by dialogue beats, action beats, reaction beats, reveal beats and silence—not arbitrary equal clip lengths.",
        "Do not force a cut. A shot may hold through multiple dialogue lines when performance and geography benefit from staying present.",
        "When actual TTS duration becomes available, rescale or re-time shot boundaries while preserving editorial beat order.",
        "For 3D scenes, preserve established 3D visual language; never convert to live action unless explicitly requested.",
    ])


def build_cinematic_shot_timeline(episode: dict, scene: dict, scene_index: int = 0) -> list[dict[str, Any]]:
    """Build a deterministic timing baseline using dialogue/action/reaction beats."""
    total = _estimate_scene_duration(scene)
    dialogue = build_dialogue_timeline(scene)
    timeline: list[dict[str, Any]] = []
    if not dialogue:
        return [{
            "shot": 1, "start": 0.0, "end": round(total, 2), "duration": round(total, 2),
            "size": "wide/medium master", "angle": "eye level", "lens": "wide-normal",
            "subject": "scene", "purpose": "establish geography and follow meaningful action without unnecessary cutting",
            "movement": "motivated slow push or locked-off hold", "cut_reason": "end of scene or meaningful change of attention",
        }]

    first_start = max(0.0, min(float(dialogue[0]["start"]), 2.5))
    if first_start > 0.15:
        timeline.append({
            "shot": 1, "start": 0.0, "end": round(first_start, 2), "duration": round(first_start, 2),
            "size": "wide establishing", "angle": "eye level", "lens": "wide", "subject": "scene geography",
            "purpose": "orient the audience before the first spoken beat", "movement": "locked-off or restrained establishing movement",
            "cut_reason": "first dialogue/action beat begins",
        })

    shot_no = len(timeline) + 1
    speakers: list[str] = []
    for turn in dialogue:
        if turn["speaker"] not in speakers:
            speakers.append(turn["speaker"])
    for i, turn in enumerate(dialogue):
        start, end, speaker = float(turn["start"]), float(turn["end"]), turn["speaker"]
        timeline.append({
            "shot": shot_no, "start": round(start, 2), "end": round(end, 2), "duration": round(max(0.0, end-start), 2),
            "size": "medium close-up" if len(dialogue) <= 4 else "over-the-shoulder / medium", "angle": "eye level", "lens": "normal",
            "subject": speaker, "purpose": f"deliver turn {turn['turn']} while showing the speaker's intention and performance",
            "movement": "subtle motivated hold or slow push only if emotion escalates", "eyeline": "toward listener / correct target",
            "cut_reason": "completed thought or next meaningful reaction",
        })
        shot_no += 1
        pause = float(turn.get("pause_after", 0.25))
        next_start = float(dialogue[i + 1]["start"]) if i + 1 < len(dialogue) else total
        reaction_end = min(next_start, end + pause)
        if reaction_end - end >= 0.12:
            listener = next((x for x in speakers if x != speaker), "listener")
            timeline.append({
                "shot": shot_no, "start": round(end, 2), "end": round(reaction_end, 2), "duration": round(reaction_end-end, 2),
                "size": "reaction close-up" if len(dialogue) <= 4 else "reaction medium close-up", "angle": "reverse angle / OTS", "lens": "normal-long",
                "subject": listener, "purpose": "allow the listener to process the line and reveal emotional consequence",
                "movement": "hold; micro-expression and breathing carry the beat", "eyeline": "toward active speaker",
                "cut_reason": "listener response completes or next speaker begins",
            })
            shot_no += 1
    if timeline:
        timeline[-1]["end"] = round(total, 2)
        timeline[-1]["duration"] = round(max(0.0, total - float(timeline[-1]["start"])), 2)
    return timeline


def build_cinematic_shot_plan(episode: dict, scene: dict, scene_index: int = 0) -> list[dict[str, Any]]:
    return build_cinematic_shot_timeline(episode, scene, scene_index)
