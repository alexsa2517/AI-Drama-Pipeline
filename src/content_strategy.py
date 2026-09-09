from __future__ import annotations

from typing import Any


CHANNEL_NAME = "MYTHIC ARCHIVES"
STORY_SCORE_THRESHOLD = 75


def score_story(candidate: dict[str, Any]) -> dict[str, Any]:
    """Deterministic pre-production score for MYTHIC ARCHIVES story candidates.

    Scores are editorial gates, not a prediction of YouTube performance.
    Each component is expected to be 0-100.
    """
    weights = {
        "hook": 25,
        "curiosity": 20,
        "emotional_impact": 15,
        "myth_significance": 15,
        "visual_potential": 15,
        "originality": 10,
    }

    scores = {key: max(0, min(100, int(candidate.get(key, 0)))) for key in weights}
    total = sum(scores[key] * weight for key, weight in weights.items()) / 100

    return {
        "channel": CHANNEL_NAME,
        "score": round(total, 1),
        "threshold": STORY_SCORE_THRESHOLD,
        "pass": total >= STORY_SCORE_THRESHOLD,
        "components": scores,
    }


def classify_claim(claim_type: str) -> str:
    """Normalize an editorial claim label used in episode research notes."""
    allowed = {"FACT", "TRADITION", "INTERPRETATION", "DRAMATIZATION"}
    value = str(claim_type).strip().upper()
    if value not in allowed:
        raise ValueError(f"Unsupported claim type: {claim_type}")
    return value


def build_retention_plan() -> list[dict[str, str]]:
    """Return the default Shorts narrative beats for the channel."""
    return [
        {"beat": "hook", "time": "0-3s", "goal": "Stop the scroll with a mystery, threat, or impossible claim."},
        {"beat": "mystery", "time": "3-10s", "goal": "Create a question the viewer wants answered."},
        {"beat": "escalation", "time": "10-25s", "goal": "Increase stakes and reveal meaningful myth details."},
        {"beat": "reveal", "time": "25-40s", "goal": "Deliver the central mythic reveal."},
        {"beat": "meaning", "time": "40-52s", "goal": "Explain why the story matters or add a twist."},
        {"beat": "open_loop", "time": "52-60s", "goal": "Leave a truthful, relevant reason to explore another myth."},
    ]
