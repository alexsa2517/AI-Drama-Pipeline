from src.legend_fact_engine import build_fact_first_policy, build_research_prompt, build_story_guardrail_prompt, validate_claims


def test_unsupported_claim_is_blocked():
    result = validate_claims([
        {"claim": "A king flew to the moon", "category": "historical_fact", "allowed_for_script": True}
    ])
    assert result["valid"] is False
    assert "A king flew to the moon" in result["blocked_claims"]


def test_sourced_legend_claim_can_be_allowed():
    result = validate_claims([
        {
            "claim": "The tradition says the hero defeated the serpent",
            "category": "traditional_legend",
            "source": "Reputable reference work",
            "source_url": "https://example.org/reference",
            "evidence": "The source records this as a traditional account.",
            "confidence": "medium",
            "allowed_for_script": True,
        }
    ])
    assert result["valid"] is True
    assert result["allowed_claims"]


def test_prompts_for_provenance_and_no_invention():
    policy = build_fact_first_policy()
    research = build_research_prompt("Baba Yaga", "Russia / Eastern Europe")
    guardrail = build_story_guardrail_prompt()
    for text in (policy, research, guardrail):
        assert "Never fill missing evidence with plausible details." in text or "never invent" in text.lower()
        assert "source" in text.lower()
