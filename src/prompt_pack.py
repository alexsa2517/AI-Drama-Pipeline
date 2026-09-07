from __future__ import annotations

from .continuity import build_character_context, scene_continuity_context
from .prompt_builder import build_image_prompt, build_video_prompt, build_voice_prompt


def build_scene_pack(episode: dict) -> list[dict]:
    character_context = build_character_context(episode)
    packs = []
    for index, scene in enumerate(episode.get("scenes", [])):
        packs.append({
            "scene_id": scene["id"],
            "image": build_image_prompt(episode, scene) + "\n\n" + character_context,
            "video": build_video_prompt(episode, scene) + "\n\n" + scene_continuity_context(episode, index),
            "voice": build_voice_prompt(episode, scene),
        })
    return packs
