from __future__ import annotations

from .feature_film_motion import motion_quality_issues
from .ai_sound_director import build_sound_cue_timeline
from .ai_cinematic_director import build_cinematic_shot_plan
from .hook_pacing_director import build_hook_3_stage_plan, pacing_structure_report


def score_hook(text: str) -> int:
    if not text:
        return 0
    score = 40
    length = len(text)
    if 40 <= length <= 180: score += 20
    if any(x in text.lower() for x in ["but", "until", "then", "why", "กลับ", "แต่", "จน", "ทำไม"]): score += 15
    if any(x in text.lower() for x in ["danger", "secret", "shadow", "voice", "อันตราย", "ความลับ", "เสียง", "เงา"]): score += 15
    if any(x in text for x in ["...", "?", "!", "…"]): score += 10
    return min(score, 100)


def story_structure_report(episode: dict) -> dict:
    scenes = episode.get("scenes", [])
    if not scenes: return {"score": 0, "issues": ["No scenes available for story structure analysis"]}
    issues = []
    first, last = scenes[0], scenes[-1]
    first_text = " ".join(str(first.get(k, "")) for k in ("title", "action", "narration", "story_purpose", "story_question", "reveal")).lower()
    last_text = " ".join(str(last.get(k, "")) for k in ("title", "action", "narration", "story_purpose", "reveal", "payoff")).lower()
    if not any(x in first_text for x in ["?", "!", "...", "…", "mystery", "danger", "secret", "shadow", "voice", "อันตราย", "ความลับ", "เสียง", "เงา", "ทำไม"]): issues.append("Opening scene has no clear hook marker or mystery/danger signal")
    if len(scenes) >= 3:
        middle = scenes[len(scenes) // 2]
        text = " ".join(str(middle.get(k, "")) for k in ("action", "story_purpose", "conflict", "reveal", "emotional_beat")).lower()
        if not any(x in text for x in ["conflict", "danger", "reveal", "choice", "threat", "turn", "escalat", "ความขัดแย้ง", "อันตราย", "เปิดเผย", "ทางเลือก", "ภัย"]): issues.append("Middle section has no explicit escalation/reveal/choice signal")
    else: issues.append("Story has fewer than 3 scenes; beginning/middle/ending cannot be strongly separated")
    if not any(x in last_text for x in ["payoff", "climax", "reveal", "resolve", "resolution", "ending", "final", "เฉลย", "จุดไคลแมกซ์", "บทสรุป", "ตอนจบ"]): issues.append("Final scene has no explicit climax/reveal/payoff signal")
    return {"score": max(0, 100 - len(issues) * 25), "issues": issues}


def hook_pacing_report(episode: dict) -> dict:
    hook = build_hook_3_stage_plan(episode)
    pacing = pacing_structure_report(episode)
    issues = list(hook["issues"]) + list(pacing["issues"])
    score = min(hook["score"], pacing["score"])
    return {"score": score, "issues": issues, "hook_3_stage": hook["stages"], "scene_decisions": pacing["scene_decisions"]}


def continuity_issues(episode: dict) -> list[str]:
    issues = []
    chars = {c.get("id") for c in episode.get("characters", [])}
    if not chars: issues.append("No character bible entries found")
    for scene in episode.get("scenes", []):
        for ref in scene.get("characters", []):
            if ref not in chars: issues.append(f"{scene.get('id')}: unknown character {ref}")
        if not scene.get("action"): issues.append(f"{scene.get('id')}: missing action")
    return issues


def motion_structure_report(episode: dict) -> dict:
    warnings = motion_quality_issues(episode)
    hard_failures = [x for x in warnings if "missing action" in x.lower()]
    missing_intent = [x for x in warnings if "no explicit movement intent" in x.lower()]
    return {"score": max(0, 100 - len(hard_failures) * 25 - len(missing_intent) * 10), "issues": warnings, "hard_failures": hard_failures, "warnings": missing_intent}


def sound_structure_report(episode: dict) -> dict:
    scenes = episode.get("scenes", [])
    if not scenes: return {"score": 0, "issues": ["No scenes available for sound analysis"]}
    issues = []
    cue_count = 0
    for scene in scenes:
        cues = build_sound_cue_timeline(episode, scene)
        cue_count += len(cues)
        if not scene.get("location"): issues.append(f"{scene.get('id')}: missing location for natural ambience")
        if not cues: issues.append(f"{scene.get('id')}: no sound cue plan generated")
    score = max(0, 100 - len(issues) * 20)
    return {"score": score, "issues": issues, "cue_count": cue_count}


def _timeline_issues(plan: list[dict], expected_end: float) -> list[str]:
    issues = []
    if not plan:
        return ["No cinematic shot timeline generated"]
    if abs(float(plan[0].get("start", 0.0))) > 0.01:
        issues.append("Cinematic timeline does not start at 0.00s")
    previous_end = 0.0
    for shot in plan:
        start = float(shot.get("start", -1))
        end = float(shot.get("end", -1))
        duration = float(shot.get("duration", -1))
        if start < -0.001 or end <= start:
            issues.append(f"SHOT {shot.get('shot')}: invalid start/end")
            continue
        if abs((end - start) - duration) > 0.03:
            issues.append(f"SHOT {shot.get('shot')}: duration does not match start/end")
        if start < previous_end - 0.03:
            issues.append(f"SHOT {shot.get('shot')}: overlaps previous shot")
        elif start > previous_end + 0.03:
            issues.append(f"SHOT {shot.get('shot')}: gap before shot")
        previous_end = end
        for required in ("purpose", "cut_reason"):
            if not shot.get(required):
                issues.append(f"SHOT {shot.get('shot')}: missing {required}")
    if abs(previous_end - expected_end) > 0.05:
        issues.append(f"Cinematic timeline ends at {previous_end:.2f}s but expected {expected_end:.2f}s")
    return issues


def cinematic_structure_report(episode: dict) -> dict:
    scenes = episode.get("scenes", [])
    if not scenes: return {"score": 0, "issues": ["No scenes available for cinematic directing analysis"]}
    issues = []
    shot_count = 0
    for scene in scenes:
        plan = build_cinematic_shot_plan(episode, scene)
        shot_count += len(plan)
        expected_end = max([float(x.get("end", 0.0)) for x in plan], default=0.0)
        issues.extend(f"{scene.get('id')}: {issue}" for issue in _timeline_issues(plan, expected_end))
        if not scene.get("location"): issues.append(f"{scene.get('id')}: missing location for spatial cinematography")
        if not scene.get("action") and not scene.get("dialogue_lines") and not scene.get("dialogue"): issues.append(f"{scene.get('id')}: no action/dialogue basis for shot motivation")
    score = max(0, 100 - len(issues) * 15)
    return {"score": score, "issues": issues, "shot_count": shot_count}


def quality_report(episode: dict) -> dict:
    hook = score_hook(episode.get("logline", ""))
    structure = story_structure_report(episode)
    hook_pacing = hook_pacing_report(episode)
    continuity = continuity_issues(episode)
    motion = motion_structure_report(episode)
    sound = sound_structure_report(episode)
    cinematic = cinematic_structure_report(episode)
    issues = continuity + structure["issues"] + hook_pacing["issues"] + motion["issues"] + sound["issues"] + cinematic["issues"]
    return {
        "hook_score": hook,
        "hook_3_stage_score": hook_pacing["score"],
        "hook_3_stage": hook_pacing["hook_3_stage"],
        "pacing_score": hook_pacing["score"],
        "pacing_scene_decisions": hook_pacing["scene_decisions"],
        "hook_pacing_issues": hook_pacing["issues"],
        "story_structure_score": structure["score"],
        "story_structure_issues": structure["issues"],
        "motion_score": motion["score"],
        "motion_issues": motion["issues"],
        "motion_hard_failures": motion["hard_failures"],
        "motion_warnings": motion["warnings"],
        "sound_score": sound["score"],
        "sound_issues": sound["issues"],
        "sound_cue_count": sound["cue_count"],
        "cinematic_score": cinematic["score"],
        "cinematic_issues": cinematic["issues"],
        "cinematic_shot_count": cinematic["shot_count"],
        "continuity_score": max(0, 100 - len(continuity) * 20),
        "issues": issues,
        "ready": hook >= 60 and hook_pacing["score"] >= 60 and structure["score"] >= 50 and motion["score"] >= 50 and sound["score"] >= 50 and cinematic["score"] >= 50 and not continuity and not motion["hard_failures"],
    }
