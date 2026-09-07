from src.continuity import build_scene_visual_lock, scene_continuity_context
from src.prompt_pack import build_scene_pack


def test_visual_lock_keeps_exact_company_location():
    scene = {
        "id": "SC-001",
        "location": "บริษัท ABC ชั้น 15 ห้องประชุมใหญ่",
        "time": "กลางคืน",
        "action": "ชายสองคนกำลังเผชิญหน้ากัน",
    }
    prompt = build_scene_visual_lock(scene)
    assert "EXACT LOCATION: บริษัท ABC ชั้น 15 ห้องประชุมใหญ่" in prompt
    assert "same physical environment" in prompt
    assert "Do not turn an office into a street" in prompt


def test_current_location_overrides_previous_location():
    episode = {
        "scenes": [
            {"id": "SC-000", "location": "ถนนหน้าบริษัท", "action": "เดินเข้าบริษัท"},
            {"id": "SC-001", "location": "บริษัท ABC ห้องประชุม", "action": "เริ่มสนทนา"},
        ]
    }
    prompt = scene_continuity_context(episode, 1)
    assert "CURRENT SCENE LOCATION (AUTHORITATIVE): บริษัท ABC ห้องประชุม" in prompt
    assert "NEVER copy a previous location" in prompt


def test_scene_pack_contains_visual_lock_for_image_and_video():
    episode = {
        "characters": [
            {
                "id": "CHAR-001",
                "name": "A",
                "role": "manager",
                "appearance": "ชายวัย 35 ผมดำ เสื้อเชิ้ตดำ",
            }
        ],
        "scenes": [
            {
                "id": "SC-001",
                "location": "บริษัท ABC ห้องทำงาน",
                "time": "กลางคืน",
                "action": "นั่งคุยกัน",
                "speaker": "CHAR-001",
                "dialogue": "เราต้องคุยกัน",
            }
        ],
    }
    pack = build_scene_pack(episode)[0]
    assert "HARD SCENE VISUAL LOCK" in pack["visual_lock"]
    assert "บริษัท ABC ห้องทำงาน" in pack["image"]
    assert "บริษัท ABC ห้องทำงาน" in pack["video"]
    assert pack["visual_lock"] in pack["image"]
    assert pack["visual_lock"] in pack["video"]
