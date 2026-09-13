from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class LegendClaim:
    claim: str
    category: str  # historical_fact | traditional_legend | interpretation | disputed | fictionalized
    source: str = ""
    source_url: str = ""
    evidence: str = ""
    confidence: str = "unknown"  # high | medium | low | unknown
    allowed_for_script: bool = False


def build_fact_first_policy() -> str:
    return """FACT-FIRST LEGEND POLICY
- Never invent historical facts, dates, people, places, events, quotations, rituals, artifacts, or cultural practices.
- Separate historical fact from traditional legend, oral tradition, later interpretation, disputed claims, and deliberate dramatization.
- Every factual claim used in the final script must have a source reference or be explicitly marked as traditional legend/uncertain.
- Prefer primary sources, museums, universities, libraries, government/cultural institutions, academic publications, and reputable reference works.
- Do not upgrade a legend into a fact because it is repeated online.
- When sources disagree, preserve the disagreement instead of selecting a convenient version.
- Unknown is not permission to invent. Replace unsupported detail with a clearly labeled narrative transition or omit it.
- Fictional dialogue may be created for storytelling, but it must not be presented as a historical quotation unless a source verifies the quotation.
- Historical characters may speak invented dialogue only when the script labels it as dramatization in metadata.
- Never fabricate citations, books, manuscripts, dates, archaeological findings, eyewitnesses, or named scholars.
- The final story must retain a provenance trail from every factual claim to its evidence.
"""


def validate_claims(claims: list[dict[str, Any]]) -> dict[str, Any]:
    normalized: list[LegendClaim] = []
    blocked = []
    allowed = []
    for raw in claims:
        claim = LegendClaim(
            claim=str(raw.get("claim", "")).strip(),
            category=str(raw.get("category", "unknown")).strip(),
            source=str(raw.get("source", "")).strip(),
            source_url=str(raw.get("source_url", "")).strip(),
            evidence=str(raw.get("evidence", "")).strip(),
            confidence=str(raw.get("confidence", "unknown")).strip(),
            allowed_for_script=bool(raw.get("allowed_for_script", False)),
        )
        fact_like = claim.category in {"historical_fact", "disputed", "traditional_legend", "interpretation"}
        has_provenance = bool(claim.source or claim.source_url or claim.evidence)
        claim.allowed_for_script = bool(claim.allowed_for_script and fact_like and has_provenance)
        normalized.append(claim)
        (allowed if claim.allowed_for_script else blocked).append(claim.claim)

    return {
        "valid": not blocked,
        "claims": [asdict(c) for c in normalized],
        "allowed_claims": allowed,
        "blocked_claims": blocked,
        "policy": "fact-first",
    }


def build_research_prompt(topic: str, country: str = "") -> str:
    return "\n".join([
        "FACT-FIRST LEGEND RESEARCHER",
        f"Topic: {topic}",
        f"Country/region: {country or 'not specified'}",
        "Research before writing. Do not draft the story until a source-backed claim ledger exists.",
        "Return claims in separate buckets: HISTORICAL FACT, TRADITIONAL LEGEND, DISPUTED/UNCERTAIN, INTERPRETATION, and FICTIONALIZED DRAMATIZATION.",
        "For every claim provide: exact claim, category, source title, source URL or bibliographic reference, evidence summary, confidence, and whether it is safe to use in the script.",
        "Use multiple independent reputable sources where feasible. Flag source conflicts explicitly.",
        "Never fill missing evidence with plausible details.",
    ])


def build_story_guardrail_prompt() -> str:
    return "\n".join([
        "LEGEND STORY GUARDRAIL",
        build_fact_first_policy(),
        "Before finalization, perform a provenance audit: every historical-looking statement must map to a research claim.",
        "If a scene requires an unsupported detail, rewrite the scene so it does not assert that detail.",
        "Keep invented dialogue and cinematic staging clearly distinguishable from sourced history.",
        "Preserve the mystery and drama without manufacturing evidence.",
    ])
