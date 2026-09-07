from src.two_character_dialogue import build_two_character_timeline, build_two_character_prompt


def test_two_character_turns_assign_listener():
    scene = {
        'location': 'บริษัท ABC ชั้น 15 ห้องประชุมใหญ่',
        'dialogue_lines': [
            {'speaker': 'CHAR-001', 'dialogue': 'คุณรู้เรื่องนี้ไหม', 'pause_after': 0.3},
            {'speaker': 'CHAR-002', 'dialogue': 'ฉันเพิ่งรู้', 'pause_after': 0.3},
        ],
    }
    timeline = build_two_character_timeline(scene)
    assert timeline[0]['speaker'] == 'CHAR-001'
    assert timeline[0]['listener'] == 'CHAR-002'
    assert timeline[1]['speaker'] == 'CHAR-002'
    assert timeline[1]['listener'] == 'CHAR-001'


def test_prompt_locks_one_environment_and_speaker_mouth():
    scene = {
        'location': 'บริษัท ABC ชั้น 15 ห้องประชุมใหญ่',
        'dialogue_lines': [
            {'speaker': 'CHAR-001', 'dialogue': 'คุณรู้เรื่องนี้ไหม'},
            {'speaker': 'CHAR-002', 'dialogue': 'ฉันเพิ่งรู้'},
        ],
    }
    prompt = build_two_character_prompt(scene)
    assert 'ABSOLUTE LOCATION LOCK: บริษัท ABC ชั้น 15 ห้องประชุมใหญ่' in prompt
    assert 'Only the active speaker moves their mouth' in prompt
    assert 'The listener remains silent' in prompt
    assert 'SPEAKER=CHAR-001' in prompt
    assert 'SPEAKER=CHAR-002' in prompt
