from __future__ import annotations

from .feature_film_motion import motion_quality_issues


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


def story_structure_report(episode: dict) -> dict:
    """Deterministic structural checks for hook, beginning, middle and ending."""
    scenes = episode.get("scenes", [])
    if not scenes:
        return {"score": 0, "issues": ["No scenes available for story structure analysis"]}

    issues = []
    first = scenes[0]
    last = scenes[-1]
    first_text = " ".join(str(first.get(k, "")) for k in ("title", "action", "narration", "story_purpose", "story_question", "reveal")).lower()
    last_text = " ".join(str(last.get(k, "")) for k in ("title", "action", "narration", "story_purpose", "reveal", "payoff")).lower()

    hook_markers = ["?", "!", "...", "…", "mystery", "danger", "secret", "shadow", "voice", "อันตราย", "ความลับ", "เสียง", "เงา", "ทำไม"]
    if not any(marker in first_text for marker in hook_markers):
        issues.append("Opening scene has no clear hook marker or mystery/danger signal")

    if len(scenes) >= 3:
        middle = scenes[len(scenes) // 2]
        middle_text = " ".join(str(middle.get(k, "")) for k in ("action", "story_purpose", "conflict", "reveal", "emotional_beat")).lower()
        escalation_markers = ["conflict", "danger", "reveal", "choice", "threat", "turn", "escalat", "ความขัดแย้ง", "อันตราย", "เปิดเผย", "ทางเลือก", "ภัย"]
        if not any(marker in middle_text for marker in escalation_markers):
            issues.append("Middle section has no explicit escalation/reveal/choice signal")
    else:
        issues.append("Story has fewer than 3 scenes; beginning/middle/ending cannot be strongly separated")

    ending_markers = ["payoff", "climax", "reveal", "resolve", "resolution", "ending", "final", "เฉลย", "จุดไคลแมกซ์", "บทสรุป", "ตอนจบ"]
    if not any(marker in last_text for marker in ending_markers):
        issues.append("Final scene has no explicit climax/reveal/payoff signal")

    score = max(0, 100 - len(issues) * 25)
    return {"score": score, "issues": issues}


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


def motion_structure_report(episode: dict) -> dict:
    """Check whether scenes provide enough information for believable natural motion."""
    scenes = episode.get("scenes", [])
    if not scenes:
        return {"score": 0, "issues": ["No scenes available for motion analysis"]}

    warnings = motion_quality_issues(episode)
    hard_failures = [issue for issue in warnings if "missing action" in issue.lower()]
    missing_intent = [issue for issue in warnings if "no explicit movement intent" in issue.lower()]
    score = max(0, 100 - len(hard_failures) * 25 - len(missing_intent) * 10)
    return {
        "score": score,
        "issues": warnings,
        "hard_failures": hard_failures,
        "warnings": missing_intent,
    }


def quality_report(episode: dict) -> dict:
    logline = episode.get("logline", "")
    hook = score_hook(logline)
    structure = story_structure_report(episode)
    continuity = continuity_issues(episode)
    motion = motion_structure_report(episode)
    issues = continuity + structure["issues"] + motion["issues"]
    return {
        "hook_score": hook,
        "story_structure_score": structure["score"],
        "story_structure_issues": structure["issues"],
        "motion_score": motion["score"],
        "motion_issues": motion["issues"],
        "motion_hard_failures": motion["hard_failures"],
        "motion_warnings": motion["warnings"],
        "continuity_score": max(0, 100 - len(continuity) * 20),
        "issues": issues,
        "ready": hook >= 60 and structure["score"] >= 50 and motion["score"] >= 50 and not continuity and not motion["hard_failures"],
    }
