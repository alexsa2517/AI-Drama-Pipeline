from __future__ import annotations

"""Feature-film natural motion direction.

Provider-neutral motion rules for believable human movement, secondary motion,
weight transfer, gaze, gesture, and shot-to-shot motion continuity.
"""

MOTION_MASTER = """FEATURE-FILM NATURAL CHARACTER MOTION SYSTEM
- Characters move like real human performers with believable weight, balance, inertia and intention.
- Every movement must have a reason: attention, emotion, dialogue, environment, obstacle or goal.
- Prefer subtle layered motion over constant full-body animation.
- Preserve physical continuity: feet contact the ground, joints articulate naturally, body mass transfers correctly, and objects respond to contact and force.
- Use anticipation -> action -> follow-through -> settle. Never snap instantly between poses.
- Maintain believable acceleration and deceleration; no robotic linear motion, sudden teleporting or frictionless sliding.
- Human asymmetry is required: left/right sides should not move as mirrored mechanical copies.
- Add micro-movements: breathing, posture adjustment, eye saccades, small balance corrections and natural stillness.
- Stillness is intentional acting, not a frozen frame.
- Secondary motion follows primary motion with believable delay: hair, cloth, sleeves, jewelry and carried objects respond to inertia and gravity.
- Do not add movement merely to make the clip look busy.
"""

BODY_RULES = """BODY MECHANICS
- Head, neck, shoulders, spine, pelvis, knees, ankles and feet form one connected kinetic chain.
- When turning, the eyes usually lead, then head, shoulders and torso follow as appropriate.
- When reaching, shift balance before or during the reach; do not stretch from a locked torso.
- When walking, use believable stride length, foot placement, heel/toe behavior, pelvis rotation and counter-swing of the arms.
- When stopping, decelerate and allow a small settling motion rather than freezing instantly.
- When sitting or standing, show weight transfer and interaction with the chair/floor.
- Hands and fingers remain anatomically coherent; gestures start and finish naturally and do not loop.
"""

EMOTION_RULES = """EMOTION TO MOTION
- Calm: economical movement, relaxed posture, smooth breathing and small weight shifts.
- Fear: attention leads movement; brief hesitation, guarded posture, cautious weight transfer and motivated recoil.
- Suspicion: restrained movement, inspection, small head tilt and controlled repositioning.
- Anger: grounded stance, deliberate movement, contained muscular tension; avoid cartoon aggression.
- Sadness: reduced movement, slower transitions, heavier posture and longer settling.
- Urgency: faster but physically plausible transitions, purposeful steps and compressed pauses.
- Awe/wonder: attention and gaze lead; movement may slow as the character processes what they see.
"""

CAMERA_INTERACTION = """CHARACTER-CAMERA INTERACTION
- Movement must remain coherent with framing, lens perspective and screen direction.
- Do not let a character drift through the frame because of generation artifacts.
- Preserve eye-line and target position when the camera changes angle.
- Camera movement and character movement must feel motivated and physically compatible.
- Keep feet, hands and body inside plausible spatial relationships with the environment.
"""

NEGATIVE = """MOTION ARTIFACT SUPPRESSION
Avoid: robotic looping, synchronized body motion, rubber limbs, floating feet, foot sliding, skating, teleporting,
instant pose changes, broken joints, hyper-flexible wrists, duplicated fingers, fused hands, stiff shoulders,
head wobble, unnatural spine bending, weightless movement, constant gesturing, repeated gestures, cloth/hair
moving independently of the body, impossible object interaction, collision errors, temporal flicker, identity drift,
pose reset between cuts, and movement without narrative motivation.
"""


def _emotion(scene: dict) -> str:
    return str(scene.get("emotion") or scene.get("emotional_beat") or "natural").strip()


def _movement(scene: dict) -> str:
    return str(scene.get("movement") or scene.get("character_movement") or scene.get("action") or "natural scene-appropriate movement").strip()


def build_feature_film_motion_prompt(episode: dict, scene: dict) -> str:
    """Build a complete motion block for image/video generation."""
    characters = scene.get("characters") or []
    lines = [
        MOTION_MASTER,
        BODY_RULES,
        EMOTION_RULES,
        CAMERA_INTERACTION,
        f"SCENE MOVEMENT INTENT: {_movement(scene)}",
        f"SCENE EMOTION: {_emotion(scene)}",
        f"CHARACTERS IN MOTION: {', '.join(map(str, characters)) if characters else 'all visible characters'}",
        "PERFORMANCE RULE: establish the character's current pose/state first, then execute movement progressively; preserve the ending state for the next shot.",
        "LISTENER RULE: a non-speaking character remains physically alive through breathing, gaze, balance and subtle reactions, but does not perform distracting gestures.",
        "SPEAKER RULE: dialogue movement supports intention and does not become repetitive hand-waving.",
        NEGATIVE,
    ]
    return "\n".join(lines)


def build_motion_continuity_prompt(episode: dict, scene_index: int) -> str:
    """Create shot-to-shot motion continuity instructions."""
    scenes = episode.get("scenes", [])
    current = scenes[scene_index] if 0 <= scene_index < len(scenes) else {}
    previous = scenes[scene_index - 1] if scene_index > 0 else {}
    if not previous:
        return "MOTION CONTINUITY: establish the first scene's baseline pose, gaze target, stance and movement state."
    return "\n".join([
        "MOTION CONTINUITY ACROSS SCENES",
        f"PREVIOUS SCENE STATE: action={previous.get('action', '')}; movement={previous.get('movement', previous.get('character_movement', ''))}; emotion={previous.get('emotion', previous.get('emotional_beat', ''))}",
        f"CURRENT SCENE STATE: action={current.get('action', '')}; movement={current.get('movement', current.get('character_movement', ''))}; emotion={current.get('emotion', current.get('emotional_beat', ''))}",
        "If the same character continues across the cut, preserve plausible pose, weight, gaze direction, momentum and emotional residue.",
        "Do not reset the character to a neutral standing pose unless the story explicitly requires a reset.",
        "If time or location changes, transition the physical state deliberately rather than teleporting the body.",
    ])


def motion_quality_issues(episode: dict) -> list[str]:
    """Deterministic motion QA for episode data; absence of explicit motion is flagged, not treated as failure of rendering."""
    issues: list[str] = []
    scenes = episode.get("scenes", [])
    for scene in scenes:
        if not scene.get("action"):
            issues.append(f"{scene.get('id')}: missing action for motion direction")
        if not (scene.get("movement") or scene.get("character_movement")):
            issues.append(f"{scene.get('id')}: no explicit movement intent; natural default will be used")
    return issues
