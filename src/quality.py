from __future__ import annotations


def score_hook(text: str) -> int:
    """Simple deterministic hook score (0-100) for V1.1."""
    if not text:
        return 0
    score = 40
    length = len(text)
    if 40 <= length <= 180:
        score += 20
    if any(x in text.lower() for x in ["but", "until", "then", "why", "กลับ", "แต่", "จน", "ทำไม"]):
        score += 15
    if any(x in text.lower() for x in ["danger", "secret", "shadow", "voice", "อันตราย", "ความลับ", "เสียง", "เงา"]):
        score += 15
    if any(x in text for x in ["...", "?", "!", "…"]):
        score += 10
    return min(score, 100)


def continuity_issues(episode: dict) -> list[str]:
    issues = []
    chars = {c.get("id"): c for c in episode.get("characters", [])}
    if not chars:
        issues.append("No character bible entries found")
    for scene in episode.get("scenes", []):
        refs = scene.get("characters", [])
        for ref in refs:
            if ref not in chars:
                issues.append(f"{scene.get('id')}: unknown character {ref}")
        if not scene.get("action"):
            issues.append(f"{scene.get('id')}: missing action")
    return issues


def quality_report(episode: dict) -> dict:
    logline = episode.get("logline", "")
    hook = score_hook(logline)
    issues = continuity_issues(episode)
    return {
        "hook_score": hook,
        "continuity_score": max(0, 100 - len(issues) * 20),
        "issues": issues,
        "ready": hook >= 60 and not issues,
    }
