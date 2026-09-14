from __future__ import annotations

from .continuity import build_character_context, build_scene_visual_lock, scene_continuity_context
from .prompt_builder import build_image_prompt, build_video_prompt, build_voice_prompt
from .animation_rules import build_character_animation_context
from .ai_acting_director import build_acting_prompt
from .professional_director import build_professional_director_prompt
from .cinematography_director import build_cinematography_prompt
from .feature_film_cinema import build_feature_film_cinema_prompt
from .feature_film_audio import build_feature_film_audio_prompt
from .feature_film_story import build_legend_story_prompt, build_scene_story_prompt
from .legend_fact_engine import build_fact_first_policy, build_story_guardrail_prompt
from .dialogue_scene import build_camera_plan, build_conversation_prompt
from .speech_pipeline import build_dialogue_video_prompt
from .shot_director import build_shot_director_prompt
from .timeline import build_dialogue_timeline, build_timeline_prompt
from .audio_direction import build_audio_direction


def build_scene_pack(episode: dict) -> list[dict]:
    character_context = build_character_context(episode)
    is_legend = str(episode.get("content_type", "")).lower() == "legend" or str(episode.get("genre", "")).lower() in {"legend", "folklore", "myth", "mythology", "dark folklore thriller"}
    fact_policy = build_fact_first_policy() if is_legend else ""
    story_guardrail = build_story_guardrail_prompt() if is_legend else ""
    story_blueprint = build_legend_story_prompt(episode) if is_legend else ""
    provenance = episode.get("research_claims", [])
    provenance_text = ""
    if is_legend:
        provenance_text = "RESEARCH CLAIM LEDGER\n" + (str(provenance) if provenance else "NO CLAIM LEDGER PROVIDED — DO NOT ASSERT HISTORICAL FACTS; RESEARCH MUST PRECEDE FINAL SCRIPT.")

    packs = []
    for index, scene in enumerate(episode.get("scenes", [])):
        story_direction = build_scene_story_prompt(episode, scene, index) if is_legend else ""
        visual_lock = build_scene_visual_lock(scene)
        conversation = build_conversation_prompt(scene)
        camera_plan = build_camera_plan(scene)
        shot_director = build_shot_director_prompt(scene)
        professional_director = build_professional_director_prompt(scene)
        cinematography = build_cinematography_prompt(scene)
        feature_film = build_feature_film_cinema_prompt(episode, scene)
        timeline = build_dialogue_timeline(scene)
        timeline_prompt = build_timeline_prompt(scene)
        audio_direction = build_audio_direction(scene)
        feature_film_audio = build_feature_film_audio_prompt(episode, scene)
        dialogue_video = build_dialogue_video_prompt(episode, scene)
        acting_director = build_acting_prompt(scene)
        video_parts = [visual_lock]
        if story_direction:
            video_parts.append(story_direction)
        video_parts.extend([feature_film, build_video_prompt(episode, scene)])
        if dialogue_video:
            video_parts.append(dialogue_video)
        if conversation:
            video_parts.append(conversation)
            video_parts.append("CAMERA PLAN:\n" + "\n".join(f"- {shot}" for shot in camera_plan))
            video_parts.append(shot_director)
            video_parts.append(professional_director)
            video_parts.append(cinematography)
            video_parts.append(timeline_prompt)
        else:
            video_parts.append(cinematography)
        video_parts.append(audio_direction)
        video_parts.append(feature_film_audio)
        video_parts.append(acting_director)
        video_parts.append(build_character_animation_context(episode, scene))
        if is_legend:
            video_parts.append(story_blueprint)
            video_parts.append(fact_policy)
            video_parts.append(story_guardrail)
            video_parts.append(provenance_text)
        video_parts.append(scene_continuity_context(episode, index))
        packs.append({
            "scene_id": scene["id"],
            "visual_lock": visual_lock,
            "story_direction": story_direction,
            "story_blueprint": story_blueprint,
            "feature_film_cinema": feature_film,
            "feature_film_audio": feature_film_audio,
            "image": visual_lock + "\n\n" + (story_direction + "\n\n" if story_direction else "") + feature_film + "\n\n" + build_image_prompt(episode, scene) + "\n\n" + character_context + "\n\n" + cinematography,
            "video": "\n\n".join(video_parts),
            "voice": build_voice_prompt(episode, scene),
            "dialogue": conversation,
            "acting_director": acting_director,
            "professional_director": professional_director,
            "cinematography": cinematography,
            "camera_plan": camera_plan,
            "shot_director": shot_director,
            "dialogue_timeline": timeline,
            "audio_direction": audio_direction,
            "fact_first": is_legend,
        })
    return packs
