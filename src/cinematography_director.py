from __future__ import annotations

from typing import Any


def _text(value: Any, default: str = "") -> str:
    return str(value or default).strip()


def _infer_tone(scene: dict) -> str:
    text = " ".join([
        _text(scene.get("title")), _text(scene.get("action")),
        _text(scene.get("music_direction")), _text(scene.get("genre")),
        " ".join(_text(t.get("emotion")) for t in scene.get("dialogue_lines", []) if isinstance(t, dict)),
    ]).lower()
    if any(k in text for k in ["horror", "terror", "terrifying", "witch", "threat", "fear", "dark", "ominous", "chilling"]):
        return "dark suspense"
    if any(k in text for k in ["sad", "grief", "loss", "cry", "desperate"]):
        return "dramatic intimate"
    if any(k in text for k in ["joy", "happy", "celebration", "warm"]):
        return "warm emotional"
    if any(k in text for k in ["epic", "battle", "war", "king", "legend"]):
        return "epic cinematic"
    return "natural cinematic"


def build_lighting_bible(scene: dict) -> str:
    tone = _infer_tone(scene)
    time = _text(scene.get("time"), "scene time/conditions")
    anchor = _text(scene.get("visual_anchor"), "established environment")
    return "\n".join([
        "PROFESSIONAL LIGHTING BIBLE",
        f"Emotional lighting language: {tone}.",
        f"Time and conditions: {time}.",
        f"Established visual anchor: {anchor}.",
        "Use motivated practical sources first: fire, candle, lamp, moonlight, window light, street light or other sources explicitly present in the scene.",
        "Maintain believable key, fill and rim separation without flattening the face. Preserve natural skin tone under colored environmental light.",
        "Keep lighting direction, color temperature, shadow direction and intensity consistent across coverage unless the story explicitly motivates a change.",
        "Use negative fill and controlled shadow where appropriate for dramatic depth; never crush facial detail into unreadable black.",
        "For suspense, allow gradual contrast escalation and selective falloff rather than random exposure shifts.",
        "For emotional close-ups, prioritize readable eyes, catchlights, skin texture and subtle facial modeling.",
        "No artificial light leaks, random lens flares, impossible shadow directions, flickering exposure, or sudden daylight changes.",
    ])


def build_color_bible(scene: dict) -> str:
    tone = _infer_tone(scene)
    palettes = {
        "dark suspense": "cool blue ambient shadows + restrained warm practical highlights; neutral skin; deep but detailed blacks",
        "dramatic intimate": "soft neutral-to-warm mids; gentle contrast; restrained saturation; natural skin",
        "warm emotional": "warm amber highlights; soft neutral shadows; natural skin; moderate saturation",
        "epic cinematic": "strong complementary separation; rich controlled saturation; cinematic contrast; protected skin tones",
        "natural cinematic": "neutral daylight-balanced foundation; subtle palette separation; controlled contrast; natural skin",
    }
    return "\n".join([
        "PROFESSIONAL COLOR BIBLE",
        f"Scene palette: {palettes[tone]}.",
        "Protect skin tones and character identity across every shot.",
        "Match exposure, white balance, black level, contrast and saturation shot-to-shot before applying emotional grade.",
        "Use color contrast to separate characters from the environment, not to recolor faces unnaturally.",
        "Emotional color changes must be gradual and story-motivated; avoid LUT-like overprocessing, neon skin, crushed blacks or clipped highlights.",
        "The final grade should feel like one photographed scene, not independent AI generations.",
    ])


def build_production_design_bible(scene: dict) -> str:
    location = _text(scene.get("location"), "exact scene location")
    anchor = _text(scene.get("visual_anchor"), "established scene details")
    environment_lock = _text(scene.get("environment_lock"), "preserve established environment")
    return "\n".join([
        "PROFESSIONAL PRODUCTION DESIGN BIBLE",
        f"Location: {location}.",
        f"Visual anchor: {anchor}.",
        f"Environment lock: {environment_lock}.",
        "Treat architecture, furniture, doors, windows, practical lights, props and spatial relationships as production-design continuity assets.",
        "Use foreground, midground and background layers to create believable depth while preserving the established layout.",
        "Props must have narrative purpose and remain consistent in scale, position and condition unless the action changes them.",
        "Do not invent duplicate furniture, impossible doorways, extra windows, changing wall textures, floating objects or inconsistent room dimensions.",
        "Atmospherics such as dust, mist, rain moisture, smoke or haze must be physically motivated and remain consistent between shots.",
    ])


def build_cinematography_bible(scene: dict) -> str:
    return "\n".join([
        "PROFESSIONAL CINEMATOGRAPHY BIBLE",
        "Photograph the scene as a coherent film sequence, not as disconnected AI clips.",
        "Preserve screen direction, eyelines, character blocking and spatial geography across coverage.",
        "Choose focal length and camera distance to support dramatic intent: wider for relationship and geography, medium for interaction, close for emotional pressure.",
        "Use motivated camera movement only when it communicates attention, tension, discovery or emotional change.",
        "Maintain believable depth of field and perspective for the selected lens; do not vary optical character randomly between shots.",
        "Avoid excessive cuts. Every cut must have a narrative, emotional or editorial reason.",
        "Match horizon, headroom, eye-line height and composition across reverse angles.",
    ])


def build_cinematography_prompt(scene: dict) -> str:
    return "\n\n".join([
        build_cinematography_bible(scene),
        build_lighting_bible(scene),
        build_color_bible(scene),
        build_production_design_bible(scene),
    ])
