from src.quality import score_hook, quality_report


def test_hook_score_range():
    assert 0 <= score_hook("A mysterious voice calls his name... What happens next?") <= 100


def test_quality_report():
    episode = {
        "logline": "A mysterious voice calls his name...",
        "characters": [{"id": "CHAR-001", "name": "Hero"}],
        "scenes": [{"id": "SC001", "action": "He stops."}],
    }
    report = quality_report(episode)
    assert "hook_score" in report
    assert report["continuity_score"] == 100
