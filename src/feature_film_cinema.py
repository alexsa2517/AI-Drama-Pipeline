from __future__ import annotations

from typing import Any


def _text(value: Any, default: str = "") -> str:
    return str(value or default).strip()


FEATURE_FILM_MASTER = """FEATURE-FILM CINEMA MASTER STANDARD

Target: premium feature-film visual language, not generic AI video. The result must feel photographed and directed as one coherent production.

VISUAL REALISM
- Preserve physically plausible anatomy, materials, skin, hair, cloth, gravity, reflections and environmental interaction.
- Prefer believable imperfection over sterile AI perfection: subtle skin texture, tiny asymmetry, natural fabric behavior, restrained motion blur and realistic depth cues.
- No plastic faces, wax skin, over-sharpening, excessive HDR, videogame rendering, beauty-filter skin, random detail or synthetic glow.
- If the source style is stylized or 3D, keep the established art direction while applying feature-film cinematography, realistic lighting and physically coherent materials. Do not turn a 3D production into live action unless explicitly requested.

CINEMATIC LANGUAGE
- Think in terms of coverage for a finished feature film: establishing shot, master/two-shot, over-the-shoulder, medium, close-up, insert and reaction shot only when editorially justified.
- Establish geography before emotional close coverage. Preserve the 180-degree axis, screen direction, eyelines, blocking and relative scale.
- Use lens language intentionally: wide lenses for spatial immersion, normal lenses for natural dialogue, longer lenses for compression/isolation. Do not randomly change focal character between shots.
- Keep camera movement motivated: dolly, tracking, crane, handheld or locked-off only when it communicates story, attention or emotion. No gratuitous AI orbiting or floating-camera motion.
- Use foreground, midground and background separation for depth. Maintain believable perspective and parallax.

LIGHTING + COLOR
- Light from motivated sources present in the world. Maintain key direction, shadow logic, exposure and color temperature across coverage.
- Protect eyes and facial detail while allowing controlled contrast. Use negative fill, practicals, rim separation and atmospheric depth when motivated.
- Grade as a single photographed sequence: consistent white balance, skin tone, black level, highlight roll-off, saturation and contrast.
- Avoid clipped highlights, crushed facial shadows, neon skin, random lens flares, fake light leaks and unexplained exposure changes.

PERFORMANCE + EDITING
- Performance is priority: listen -> process -> react -> speak. Eyes lead emotion; breath and micro-expressions carry transitions.
- Do not animate every body part. Background characters and listeners remain naturally still when appropriate.
- Cut on thought, reaction, action, reveal or completed speech unit—not because a generated clip ended.
- Preserve emotional residue across cuts. Never reset expression, posture or gaze between shots without narrative cause.

AI ARTIFACT SUPPRESSION
- No identity drift, face morphing, age drift, wardrobe drift, duplicate limbs, finger anomalies, floating props, disappearing objects, geometry warping, background replacement, temporal flicker, texture crawling, lip deformation or impossible reflections.
- No random extras appearing/disappearing. Maintain continuity of props, weather, particles and environmental motion.

FINAL QUALITY BAR
The audience should notice the story and performances, not the generation process. Every shot must look intentional, physically coherent, editorially motivated and consistent with the same feature-film production bible.
"""


def build_feature_film_cinema_prompt(episode: dict, scene: dict) -> str:
    style = _text(episode.get("visual_style"), "established visual style")
    medium = _text(episode.get("render_style"), "established production medium")
    return "\n".join([
        FEATURE_FILM_MASTER,
        "PROJECT-SPECIFIC CINEMA LOCK",
        f"Visual style: {style}.",
        f"Production medium: {medium}.",
        f"Location: {_text(scene.get('location'), 'locked scene location')}.",
        f"Time/conditions: {_text(scene.get('time'), 'locked scene time and conditions')}.",
        f"Action: {_text(scene.get('action'), 'follow the approved scene action')}.",
        "Do not override established character, environment, wardrobe, dialogue, blocking or continuity locks.",
    ])
