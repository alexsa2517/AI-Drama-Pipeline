from src.story_engine import generate_story_seed


def test_story_seed_has_production_structure():
    story = generate_story_seed("A traveler enters a forbidden forest")
    assert story["logline"]
    assert len(story["characters"]) >= 1
    assert len(story["scenes"]) == 3
    assert story["scenes"][0]["id"] == "SC001"
    assert story["scenes"][-1]["title"] == "The Cliffhanger"


def test_story_seed_rejects_empty_premise():
    try:
        generate_story_seed("   ")
        assert False, "Expected ValueError"
    except ValueError:
        pass
