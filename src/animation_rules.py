from __future__ import annotations

NATURAL_EYE_RULES = """Natural eye and face animation:
- Natural blinking at irregular human intervals; never perfectly timed or robotic.
- Eyes make believable gaze shifts toward the speaker, object, threat, or point of attention.
- Do not stare into the camera unless the scene explicitly requires it.
- Use subtle saccades, eyelid movement, brow movement, and micro-expressions.
- Preserve eye color, iris shape, pupil position, facial proportions, and identity across shots.
- Emotion must appear first in the eyes and face before large body movement.
"""

SPEECH_ANIMATION_RULES = """Natural speaking animation:
- The named character is the active speaker and must visibly speak the supplied dialogue.
- Accurate lip-sync: mouth shapes, jaw, lips, cheeks, and tongue movement follow the spoken Thai words.
- Add natural pauses, breathing, swallowing, subtle head movement, and facial micro-expressions.
- Keep eye contact and gaze behavior emotionally appropriate while speaking.
- Do not let the mouth move when the character is not speaking.
- No frozen face, rubber mouth, repetitive mouth cycles, or expression reset between shots.
"""

NEGATIVE_EYE_RULES = """Avoid: crossed eyes, wandering pupils, floating eyes, duplicated pupils, malformed eyelids,
unnatural blinking, frozen stare, rapid eye jitter, sudden gaze direction changes, face warping,
identity drift, mouth deformation, incorrect lip-sync, speaking without mouth movement, and camera-facing
stare unless explicitly requested.
"""


def build_character_animation_context(episode: dict, scene: dict) -> str:
    lines = ["CHARACTER ANIMATION CONTINUITY", NATURAL_EYE_RULES, SPEECH_ANIMATION_RULES]
    dialogue = scene.get("dialogue") or ""
    speaker = scene.get("speaker") or ""
    if dialogue:
        lines.append(f"SPEAKER: {speaker or 'the active character'}")
        lines.append(f"EXACT DIALOGUE TO SPEAK: {dialogue}")
        lines.append(f"EMOTION: {scene.get('emotion') or 'natural scene-appropriate emotion'}")
        lines.append(f"DELIVERY: {scene.get('delivery') or 'natural conversational delivery'}")
    lines.append(NEGATIVE_EYE_RULES)
    return "\n".join(lines)
