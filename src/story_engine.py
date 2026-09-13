from __future__ import annotations

from typing import Any

from .legend_fact_engine import validate_claims


def generate_story_seed(
    premise: str,
    title: str = "Untitled Episode",
    genre: str = "dark fantasy",
    language: str = "th",
    content_type: str = "fiction",
    research_claims: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a deterministic story structure.

    Legend/folklore mode is fact-first: research claims are preserved as a
    provenance ledger and unsupported claims are blocked from production.
    Older fiction calls remain backward compatible.
    """
    premise = premise.strip()
    if not premise:
        raise ValueError("premise must not be empty")

    is_legend = content_type.lower() == "legend" or genre.lower() in {
        "legend", "folklore", "myth", "mythology", "dark folklore thriller"
    }
    claims = research_claims or []
    provenance = validate_claims(claims) if is_legend else {"valid": True, "claims": []}
    if is_legend and claims and not provenance["valid"]:
        raise ValueError(
            "Legend research contains unsupported claims. Blocked claims must be sourced, relabeled as traditional/disputed, or removed."
        )

    return {
        "id": "EP-AUTO-001",
        "title": title.strip() or "Untitled Episode",
        "logline": premise,
        "genre": genre,
        "language": language,
        "content_type": "legend" if is_legend else content_type,
        "fact_first": is_legend,
        "research_claims": provenance.get("claims", []),
        "characters": [
            {
                "id": "CHAR-001",
                "name": "The Protagonist",
                "role": "protagonist",
                "appearance": "consistent facial features, hairstyle, costume, and silhouette across every scene",
                "personality": "curious, cautious, determined",
                "continuity_notes": "Keep identity, costume, age, proportions, and key props consistent.",
            }
        ],
        "scenes": [
            {
                "id": "SC001",
                "title": "The Hook",
                "location": "story location to be established from research",
                "time": "time period/conditions must be sourced when historical",
                "action": f"The protagonist encounters the first sign connected to: {premise}",
                "narration": "",
                "duration_seconds": 8,
                "research_required": is_legend,
            },
            {
                "id": "SC002",
                "title": "The Discovery",
                "location": "research-backed location",
                "time": "research-backed period/conditions",
                "action": "The protagonist follows a documented or explicitly legendary clue and encounters rising danger.",
                "narration": "",
                "duration_seconds": 8,
                "research_required": is_legend,
            },
            {
                "id": "SC003",
                "title": "The Cliffhanger",
                "location": "research-backed location",
                "time": "research-backed period/conditions",
                "action": "The episode ends on a documented mystery, traditional legend element, or clearly labeled dramatization.",
                "narration": "",
                "duration_seconds": 8,
                "research_required": is_legend,
            },
        ],
    }
