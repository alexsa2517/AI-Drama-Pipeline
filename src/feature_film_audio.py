from __future__ import annotations

from .timeline import build_dialogue_timeline


FEATURE_FILM_AUDIO_MASTER = """FEATURE-FILM SOUND DESIGN MASTER

Treat sound as narrative filmmaking, not background decoration.

DIALOGUE / VOICE
- Dialogue is the primary intelligibility anchor whenever a character speaks.
- Preserve natural breaths, pauses, hesitation, emotional strain and vocal distance.
- Voice perspective must match camera distance and environment; avoid an unnaturally dry studio voice in a large space.
- Never cover important words with music or loud effects.
- Keep character voice identity consistent across scenes.

ROOM TONE / AMBIENCE
- Establish a believable acoustic world before adding music.
- Build layered ambience appropriate to location, time, weather and crowd density.
- Maintain continuous room tone between cuts so edits do not sound artificially silent.
- Ambience may subtly change with camera position, doorway transitions, interior/exterior changes and dramatic focus.

FOLEY
- Add motivated physical detail: footsteps, cloth movement, breathing, handling objects, doors, surfaces, tools and contact sounds.
- Foley timing must follow visible action precisely; do not add generic movement sounds to every gesture.
- Footsteps and object contact should reflect material, weight, speed and environment.

SOUND EFFECTS
- Use restrained, story-motivated SFX for impacts, reveals, supernatural events, weapons, weather and environmental events.
- Favor believable perspective and decay over exaggerated trailer-style effects.
- Important effects can briefly lead or trail an action when that improves dramatic clarity.

MUSIC / SCORE
- Music is optional. Silence is a deliberate cinematic tool.
- Score must support emotion, not dictate every emotion.
- Enter, change, pause and exit music around dramatic beats rather than filling the whole scene.
- Avoid constant wall-to-wall music and repetitive generic crescendos.

MIX / DYNAMICS
- Prioritize dialogue intelligibility without making every element flat or equally loud.
- Duck music and competing ambience during critical dialogue.
- Preserve dynamic range for tension, impact and quiet moments.
- Avoid clipping, pumping, harshness, excessive bass, brittle highs and artificial loudness.
- Preserve believable foreground/background perspective and distance.

SILENCE / DRAMATIC SPACE
- Use controlled silence before or after reveals, emotional reactions and important lines when appropriate.
- Silence must feel intentional and acoustically believable, not like missing audio.

AI AUDIO ARTIFACT SUPPRESSION
- No robotic cadence, metallic voice, repeated breath, duplicated footsteps, phasing, looping ambience, abrupt room-tone changes, music pumping, clipping, lip-sync mismatch or impossible sound perspective.
- Do not invent sounds for actions that are not visible or narratively justified.

FINAL FILM STANDARD
The audience should feel immersed in a coherent physical world and notice the story, performance and atmosphere—not the fact that the audio was AI-generated.
"""


def build_feature_film_audio_prompt(episode: dict, scene: dict) -> str:
    timeline = build_dialogue_timeline(scene)
    location = scene.get("location", episode.get("location", "unspecified location"))
    time_of_day = scene.get("time", scene.get("time_of_day", "unspecified time"))
    emotion = scene.get("emotion", "natural")
    delivery = scene.get("delivery", "natural conversational delivery")
    dialogue = (scene.get("dialogue") or "").strip()

    lines = [
        FEATURE_FILM_AUDIO_MASTER,
        "SCENE AUDIO BLUEPRINT",
        f"Location: {location}",
        f"Time: {time_of_day}",
        f"Primary emotion: {emotion}",
        f"Voice delivery: {delivery}",
        "Build the soundscape around the existing visual lock, blocking, camera plan and story continuity. Do not override them.",
        "Decide explicitly what is foreground, midground and background in sound.",
        "Match acoustic space, reverb, reflections and environmental noise to the physical location.",
    ]

    if dialogue:
        lines.extend([
            "DIALOGUE PRIORITY: ACTIVE",
            f"Dialogue text: {dialogue}",
            "Keep speech intelligible and preserve natural pauses; duck music and competing effects around important words.",
        ])
    else:
        lines.append("DIALOGUE PRIORITY: NONE — let ambience, foley, effects, music or silence carry the scene.")

    if timeline:
        lines.append("DRAMATIC AUDIO BEATS")
        for item in timeline:
            lines.append(
                f"TURN {item['turn']} ({item['speaker']}): {item['start']:.2f}s–{item['end']:.2f}s; "
                f"emotion={item['emotion']}; pause_after={float(item['pause_after']):.2f}s. "
                "Re-evaluate music, ambience, foley and silence around this beat."
            )

    lines.extend([
        "OUTPUT MIX PLAN:",
        "1. Dialogue / voice perspective",
        "2. Location room tone and ambience",
        "3. Motivated foley",
        "4. Story-critical SFX",
        "5. Optional score / music cue",
        "6. Dialogue ducking and dynamic balance",
        "7. Final cinematic mix and artifact QA",
    ])
    return "\n".join(lines)
