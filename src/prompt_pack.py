from __future__ import annotations

from .continuity import build_character_context, build_scene_visual_lock, scene_continuity_context
from .prompt_builder import build_image_prompt, build_video_prompt, build_voice_prompt
from .animation_rules import build_character_animation_context
from .ai_acting_director import build_acting_prompt
from .dialogue_scene import build_camera_plan, build_conversation_prompt
from .speech_pipeline import build_dialogue_video_prompt
from .shot_director import build_shot_director_prompt
from .timeline import build_dialogue_timeline, build_timeline_prompt
from .audio_direction import build_audio_direction


def build_scene_pack(episode: dict) -> list[dict]:
    character_context = build_character_context(episode)
    packs = []
    for index, scene in enumerate(episode.get("scenes", [])):
        visual_lock = build_scene_visual_lock(scene)
        conversation = build_conversation_prompt(scene)
        camera_plan = build_camera_plan(scene)
        shot_director = build_shot_director_prompt(scene)
        timeline = build_dialogue_timeline(scene)
        timeline_prompt = build_timeline_prompt(scene)
        audio_direction = build_audio_direction(scene)
        dialogue_video = build_dialogue_video_prompt(episode, scene)
        acting_director = build_acting_prompt(scene)
        video_parts = [visual_lock, build_video_prompt(episode, scene)]
        if dialogue_video:
            video_parts.append(dialogue_video)
        if conversation:
            video_parts.append(conversation)
            video_parts.append("CAMERA PLAN:\n" + "\n".join(f"- {shot}" for shot in camera_plan))
            video_parts.append(shot_director)
            video_parts.append(timeline_prompt)
        video_parts.append(audio_direction)
        video_parts.append(acting_director)
        video_parts.append(build_character_animation_context(episode, scene))
        video_parts.append(scene_continuity_context(episode, index))
        packs.append({
            "scene_id": scene["id"],
            "visual_lock": visual_lock,
            "image": visual_lock + "\n\n" + build_image_prompt(episode, scene) + "\n\n" + character_context,
            "video": "\n\n".join(video_parts),
            "voice": build_voice_prompt(episode, scene),
            "dialogue": conversation,
            "acting_director": acting_director,
            "camera_plan": camera_plan,
            "shot_director": shot_director,
            "dialogue_timeline": timeline,
            "audio_direction": audio_direction,
        })
    return packs
