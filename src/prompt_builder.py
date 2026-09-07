def build_image_prompt(episode: dict, scene: dict) -> str:
    return (
        f"Cinematic dark fantasy scene. EXACT LOCATION: {scene['location']}. "
        f"EXACT TIME: {scene['time']}. "
        f"Action: {scene['action']}. "
        "The stated location is a hard visual constraint: do not relocate, replace or reinterpret it. "
        "Maintain character identity, wardrobe, proportions and visual continuity. "
        "Preserve the same architecture, furniture, doors, windows, signage and spatial layout when established. "
        "Detailed environment, dramatic lighting, atmospheric depth, film still, "
        "high detail, coherent composition, no text, no watermark."
    )


def build_video_prompt(episode: dict, scene: dict) -> str:
    return (
        f"Animate this cinematic scene for approximately {scene.get('duration_seconds', 8)} seconds. "
        f"EXACT LOCATION: {scene['location']}. EXACT TIME: {scene['time']}. "
        f"Action: {scene['action']}. "
        "The exact location is authoritative and must remain unchanged throughout the scene. "
        "Camera angles may change, but every shot must remain inside the same physical environment. "
        "Do not transform an office/company into another setting or replace the established environment. "
        "Use subtle natural motion, controlled camera movement, consistent faces and wardrobe, "
        "physically plausible lighting, cinematic pacing, no sudden character changes, no text."
    )


def build_voice_prompt(episode: dict, scene: dict) -> str:
    return (
        f"Thai cinematic narration for scene {scene['id']}. "
        "Tone: mysterious, tense, emotional, controlled. "
        f"Narration content: {scene.get('narration') or scene['action']}"
    )
