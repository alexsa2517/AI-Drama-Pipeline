from __future__ import annotations

from typing import Any


EMOTION_PROFILES: dict[str, dict[str, str]] = {
    "natural": {
        "eyes": "soft, attentive gaze with small saccades and occasional brief gaze breaks",
        "brows": "subtle neutral brow movement",
        "mouth": "relaxed mouth between words; restrained articulation during pauses",
        "head": "small natural listening and thinking movements",
        "breath": "quiet irregular breathing with occasional natural inhale before important words",
        "blink": "irregular human blinking; avoid rhythmic blinking",
        "body": "small posture adjustments and weight shifts, never mechanical",
    },
    "fearful": {
        "eyes": "alert widened eyes, focused on the perceived threat, brief darting glances only when motivated",
        "brows": "slightly raised inner brows with tension",
        "mouth": "controlled tension around lips, brief compression between phrases",
        "head": "subtle recoil or freeze before cautious movement",
        "breath": "shallow uneven breathing with a restrained inhale before speech",
        "blink": "brief reduction in blinking during threat attention, then one natural recovery blink",
        "body": "contained tension in shoulders and neck; small defensive posture changes",
    },
    "suspicious": {
        "eyes": "narrow attentive gaze, inspect the other person's face, short side glance before returning to eye contact",
        "brows": "one-sided or asymmetric brow tension rather than symmetrical animation",
        "mouth": "slight lip press and restrained articulation",
        "head": "small head tilt or forward micro-lean while evaluating the other person",
        "breath": "quiet controlled breathing",
        "blink": "slightly less frequent during scrutiny, but still irregular and human",
        "body": "minimal movement, controlled guarded posture",
    },
    "angry": {
        "eyes": "steady focused gaze with reduced wandering; tiny eye tightening toward the target",
        "brows": "lowered tense brows with subtle asymmetry",
        "mouth": "firm lip articulation and brief lip compression after key phrases",
        "head": "small decisive movements, no exaggerated shaking",
        "breath": "deeper controlled breathing with subtle exhale after intense phrases",
        "blink": "slightly reduced blinking while confronting the target",
        "body": "contained muscular tension and deliberate stillness",
    },
    "sad": {
        "eyes": "slightly lowered gaze, moisture-like softness without artificial tears, delayed return to eye contact",
        "brows": "inner brows subtly lifted with restrained sadness",
        "mouth": "small downward tension at the corners and slower articulation",
        "head": "slight downward angle and very small movement",
        "breath": "longer exhale and occasional shaky inhale",
        "blink": "natural slower blinks with occasional longer eyelid closure",
        "body": "slumped but believable posture, subtle weight shift",
    },
    "calm": {
        "eyes": "stable warm gaze with relaxed saccades and comfortable eye contact",
        "brows": "relaxed brows with tiny reactive movements",
        "mouth": "smooth relaxed articulation and natural resting expression",
        "head": "small conversational nods only when motivated",
        "breath": "slow even breathing",
        "blink": "natural irregular blinking at relaxed intervals",
        "body": "loose posture with small natural movements",
    },
    "cold amusement": {
        "eyes": "steady knowing gaze with a tiny narrowing at the eyes; brief glance to the listener's reaction",
        "brows": "subtle asymmetric brow lift",
        "mouth": "controlled half-smile that fades between words; no constant grin",
        "head": "small confident tilt toward the listener",
        "breath": "quiet controlled breath with a soft exhale",
        "blink": "infrequent but irregular blinks, never frozen",
        "body": "still, confident posture with minimal deliberate movement",
    },
    "warning": {
        "eyes": "lock attention on the listener's eyes, then briefly glance toward the danger before returning",
        "brows": "tightened brows communicating urgency",
        "mouth": "precise restrained articulation, especially on the warning words",
        "head": "small deliberate forward movement to emphasize the warning",
        "breath": "quiet inhale before the warning and controlled exhale afterward",
        "blink": "briefly hold eye contact, then one natural blink after the warning",
        "body": "minimal movement; tension should come from stillness and focus",
    },
    "terrifying calm": {
        "eyes": "unnervingly steady gaze with tiny saccades, almost no unnecessary movement",
        "brows": "relaxed or minimally tense brows to contrast with the frightening meaning",
        "mouth": "very controlled speech with precise small mouth movement and almost no smile",
        "head": "slow measured head movement only if motivated by the final reveal",
        "breath": "quiet low breathing with a subtle pause before the most important phrase",
        "blink": "one or two precisely timed natural blinks; never continuous staring",
        "body": "near-stillness with restrained micro-movements that increase tension",
    },
}


def _find_profile(emotion: str) -> dict[str, str]:
    key = emotion.strip().lower()
    if key in EMOTION_PROFILES:
        return EMOTION_PROFILES[key]
    for profile_key, profile in EMOTION_PROFILES.items():
        if profile_key in key or key in profile_key:
            return profile
    return EMOTION_PROFILES["natural"]


def build_acting_direction(turn: dict[str, Any], previous_turn: dict[str, Any] | None = None) -> dict[str, str]:
    """Create performance-level direction for one dialogue turn.

    The result is provider-neutral and intended to be embedded into video prompts
    so each turn has motivated eye-line, blink, expression, breath, and movement.
    """
    emotion = str(turn.get("emotion", "natural"))
    profile = _find_profile(emotion)
    speaker = str(turn.get("speaker", "active speaker"))
    dialogue = str(turn.get("dialogue", "")).strip()
    previous_speaker = str(previous_turn.get("speaker", "")) if previous_turn else ""

    transition = (
        f"Respond naturally to {previous_speaker}'s previous turn; show a brief listening-to-thinking transition before speaking."
        if previous_turn and previous_speaker and previous_speaker != speaker
        else "Begin from the character's current emotional state; do not reset the expression at the cut."
    )

    return {
        "emotion": emotion,
        "eyeline": profile["eyes"],
        "brows": profile["brows"],
        "mouth": profile["mouth"],
        "head": profile["head"],
        "breath": profile["breath"],
        "blink": profile["blink"],
        "body": profile["body"],
        "transition": transition,
        "performance": (
            f"{speaker} is a professional film actor. Play the line \"{dialogue}\" with truthful intention, "
            "subtext and restraint. Avoid generic 'happy/sad/angry' acting. Let the emotion develop through the eyes, "
            "breath, tiny facial muscle changes and motivated body movement before any large gesture."
        ),
    }


def build_acting_prompt(scene: dict) -> str:
    """Build a complete actor-director block for all turns in a scene."""
    lines = [
        "PROFESSIONAL AI ACTING DIRECTOR",
        "Treat every character as a trained screen actor, not a talking avatar.",
        "Performance must have intention, subtext, listening, anticipation, reaction, restraint and continuity across cuts.",
        "Eyes lead emotion. Gaze must have a reason and a target. Never stare at the lens by default.",
        "Blinking must be irregular and motivated by attention, thought and emotion; never use a repeated animation loop.",
        "Facial expressions should evolve gradually. Do not snap from neutral to emotion or reset expression after a cut.",
        "Breathing, tiny jaw tension, swallowing, micro head movement and posture shifts should support the emotion.",
        "Use screen direction consistently. Maintain believable eyelines between characters.",
        "Listener behavior is real acting: listen, process, react internally, then prepare to respond.",
        "Do not smile unless the intention calls for it. Do not exaggerate eyebrows, nods or head movement.",
        "The mouth moves only for the active speaker and must follow the supplied audio during final lip-sync.",
    ]

    turns = scene.get("dialogue_lines") or []
    previous: dict[str, Any] | None = None
    for index, raw in enumerate(turns, 1):
        if not isinstance(raw, dict):
            continue
        turn = {
            "turn": index,
            "speaker": raw.get("speaker", "active speaker"),
            "dialogue": raw.get("dialogue", ""),
            "emotion": raw.get("emotion", "natural"),
        }
        d = build_acting_direction(turn, previous)
        lines.extend([
            f"TURN {index} — {turn['speaker']} — emotion: {d['emotion']}",
            f"Intent/performance: {d['performance']}",
            f"Eyeline: {d['eyeline']}",
            f"Brows: {d['brows']}",
            f"Mouth/face: {d['mouth']}",
            f"Head: {d['head']}",
            f"Breath: {d['breath']}",
            f"Blink: {d['blink']}",
            f"Body: {d['body']}",
            f"Transition: {d['transition']}",
        ])
        previous = turn
    return "\n".join(lines)
