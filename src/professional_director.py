from __future__ import annotations

from typing import Any

from .dialogue_scene import normalize_dialogue


DIRECTOR_BRIEF = """PROFESSIONAL CINEMA DIRECTOR
Direct the material like a serious dramatic production. The director is responsible for story clarity, blocking, eyelines, pacing, shot motivation, emotional escalation and performance continuity.

STAGING:
- Establish geography before close coverage.
- Preserve the 180-degree axis, screen direction, relative positions and lighting direction.
- Characters must have a clear objective, attention target and emotional state in every beat.

PERFORMANCE:
- Direct receive -> process -> react, not instant facial changes.
- Eyes lead emotion; breath and micro-tension precede larger movement.
- Reactions must be proportionate to the dramatic stakes.
- Silence, hesitation and withheld reactions are valid acting choices.

CAMERA:
- Every shot must have a reason: reveal, isolate, pressure, contrast, information or reaction.
- Hold longer when performance carries the scene.
- Tighten framing as psychological pressure rises.
- Use movement only when motivated by story or emotional escalation.
- Avoid generic AI camera motion and unnecessary cuts.

EDITING:
- Cut on thought changes, completed speech units, meaningful reactions or motivated pauses.
- Never cut simply because a generated clip ended.
- Preserve eyeline matches and screen direction.

CONTINUITY:
- Same physical environment, wardrobe, identity, props, light direction and character blocking unless the script explicitly changes them.
- Emotional state must carry across cuts; no unexplained reset.
"""


def _director_beat(turn: dict[str, Any]) -> dict[str, str]:
    emotion = str(turn.get("emotion", "natural")).lower()
    delivery = str(turn.get("delivery", "natural conversational delivery")).lower()
    text = str(turn.get("dialogue", ""))

    if any(k in emotion for k in ("fear", "afraid", "terrified", "panic")):
        return {"beat": "fear realization", "camera": "tight close-up or restrained push-in", "eyes": "lock on the source of danger, brief uncertainty, then refocus", "body": "small breath catch; keep movement contained"}
    if any(k in emotion for k in ("suspicious", "doubt", "uncertain")):
        return {"beat": "evaluation", "camera": "over-the-shoulder or medium close-up", "eyes": "observe, assess, briefly break gaze, return", "body": "minimal movement; subtle brow/face tension"}
    if any(k in emotion for k in ("anger", "angry", "rage")):
        return {"beat": "contained anger", "camera": "stable medium close-up, tighten only at escalation", "eyes": "fixed intent with controlled eye movement", "body": "jaw/shoulder tension before any larger gesture"}
    if any(k in emotion for k in ("sad", "grief", "desperation")):
        return {"beat": "vulnerability", "camera": "patient close-up", "eyes": "moist focus, brief avoidance, return to listener", "body": "soft exhale; restrained head and shoulder movement"}
    if any(k in emotion for k in ("cold", "ominous", "threat")):
        return {"beat": "psychological threat", "camera": "slow controlled push-in", "eyes": "calm direct gaze with minimal blink", "body": "near-stillness; tension carried by face and breath"}
    if "whisper" in delivery:
        return {"beat": "intimate whisper", "camera": "close, stable frame", "eyes": "small precise gaze shifts", "body": "low movement; audible breath and facial tension"}
    if text.endswith("?"):
        return {"beat": "question / thought exchange", "camera": "over-the-shoulder or two-shot", "eyes": "receive question, process, then answer", "body": "brief reaction delay before speech"}
    return {"beat": "natural conversational beat", "camera": "medium coverage with motivated coverage", "eyes": "maintain social eye contact with natural breaks", "body": "subtle breath, posture and head movement"}


def build_professional_director_prompt(scene: dict) -> str:
    turns = normalize_dialogue(scene)
    if not turns:
        return DIRECTOR_BRIEF

    lines = [DIRECTOR_BRIEF, "SCENE-SPECIFIC DIRECTING PLAN"]
    previous_speaker = None
    for turn in turns:
        d = _director_beat(turn)
        speaker = turn["speaker"]
        lines.append(
            f"TURN {turn['turn']} | SPEAKER={speaker} | EMOTION={turn.get('emotion', 'natural')} | DELIVERY={turn.get('delivery', 'natural conversational delivery')}"
        )
        lines.append(f"  PERFORMANCE BEAT: {d['beat']}")
        lines.append(f"  CAMERA: {d['camera']}")
        lines.append(f"  EYELINE: {d['eyes']}")
        lines.append(f"  BODY/BREATH: {d['body']}")
        if previous_speaker and previous_speaker != speaker:
            lines.append("  TRANSITION: allow the previous speaker's emotional residue to remain visible for a moment before the response; avoid instant reset")
        lines.append("  EDIT: protect the emotional beat; cut only at a motivated thought/reaction boundary")
        previous_speaker = speaker
    return "\n".join(lines)
