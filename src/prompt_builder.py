def build_image_prompt(episode: dict, scene: dict) -> str:
    return (
        f"Cinematic dark fantasy scene, {scene['location']}, {scene['time']}. "
        f"Action: {scene['action']}. "
        "Maintain character identity, wardrobe, proportions and visual continuity. "
        "Detailed environment, dramatic lighting, atmospheric depth, film still, "
        "high detail, coherent composition, no text, no watermark."
    )


def build_video_prompt(episode: dict, scene: dict) -> str:
    return (
        f"Animate this cinematic scene for approximately {scene.get('duration_seconds', 8)} seconds. "
        f"Location: {scene['location']}. Time: {scene['time']}. "
        f"Action: {scene['action']}. "
        "Use subtle natural motion, controlled camera movement, consistent faces and wardrobe, "
        "physically plausible lighting, cinematic pacing, no sudden character changes, no text."
    )


def build_voice_prompt(episode: dict, scene: dict) -> str:
    return (
        f"Thai cinematic narration for scene {scene['id']}. "
        "Tone: mysterious, tense, emotional, controlled. "
        f"Narration content: {scene.get('narration') or scene['action']}"
    )
