from src.cinematography_director import (
    build_color_bible,
    build_cinematography_prompt,
    build_lighting_bible,
    build_production_design_bible,
)


def test_lighting_bible_has_professional_controls():
    scene = {
        "location": "Baba Yaga hut",
        "time": "night",
        "visual_anchor": "fireplace left, window right, candles on table",
        "title": "dark suspense",
        "action": "A warning is delivered",
    }
    prompt = build_lighting_bible(scene)
    assert "motivated practical sources" in prompt
    assert "key, fill and rim" in prompt
    assert "shadow direction" in prompt


def test_color_bible_protects_skin_and_continuity():
    scene = {"title": "dark suspense", "action": "threat", "genre": "dark folklore thriller"}
    prompt = build_color_bible(scene)
    assert "Protect skin tones" in prompt
    assert "shot-to-shot" in prompt
    assert "cool blue ambient shadows" in prompt


def test_production_design_bible_locks_environment():
    scene = {
        "location": "old wooden hut",
        "visual_anchor": "table, fireplace, window",
        "environment_lock": "same physical environment",
    }
    prompt = build_production_design_bible(scene)
    assert "production-design continuity assets" in prompt
    assert "foreground, midground and background" in prompt
    assert "Do not invent duplicate furniture" in prompt


def test_combined_cinematography_prompt_contains_all_bibles():
    prompt = build_cinematography_prompt({
        "location": "hut",
        "time": "night",
        "visual_anchor": "fireplace and window",
        "environment_lock": "locked",
        "title": "dark suspense",
        "action": "threat",
    })
    assert "PROFESSIONAL CINEMATOGRAPHY BIBLE" in prompt
    assert "PROFESSIONAL LIGHTING BIBLE" in prompt
    assert "PROFESSIONAL COLOR BIBLE" in prompt
    assert "PROFESSIONAL PRODUCTION DESIGN BIBLE" in prompt
