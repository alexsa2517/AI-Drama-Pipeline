from __future__ import annotations

from typing import Any

HOOK_PACING_MASTER = """HOOK 3-STAGE + PACING / ANTI-FILLER DIRECTOR

HOOK
1. GRAB 0–3s: strongest available curiosity, danger, mystery, contradiction or emotional shock.
2. QUESTION 3–8s: create a specific unanswered question without explaining the whole mystery.
3. PULL 8–15s: add consequence, threat, discovery, relationship pressure or clue that makes the next beat necessary.

PACING
- Every scene must create meaningful change: information, pressure, danger, relationship movement, decision, discovery, reversal, consequence or emotional transformation.
- Every shot needs a dramatic/cinematic function. Atmosphere is valid when it creates mood, orientation, anticipation or meaning.
- If material can be removed without damaging comprehension, causality, emotion or payoff: SHORTEN, MERGE or REMOVE it.
- If silence, reaction, slow movement or an establishing shot increases tension or emotional meaning: KEEP it.
- Never accelerate merely to satisfy a numeric target.
- Enter scenes late and leave when the dramatic purpose is complete.
- Avoid repeated exposition, walking, looking, reactions and transitions.
- Choose KEEP / SHORTEN / MERGE / REMOVE / HOLD. HOLD is valid when stillness is the strongest dramatic choice.
"""


def _text(scene: dict, *keys: str) -> str:
    return " ".join(str(scene.get(k, "")) for k in keys if scene.get(k) not in (None, "")).strip()


def _has(text: str, terms: tuple[str, ...]) -> bool:
    value = text.lower()
    return any(t.lower() in value for t in terms)


def build_hook_pacing_director_prompt(episode: dict, scene: dict, scene_index: int = 0) -> str:
    scenes = episode.get("scenes", [])
    total = len(scenes)
    opening = scene_index == 0
    text = _text(scene, "title", "action", "narration", "dialogue", "story_purpose", "conflict", "reveal", "story_question")
    if opening:
        if _has(text, ("danger", "threat", "mystery", "secret", "shadow", "voice", "อันตราย", "ภัย", "ลึกลับ", "ความลับ", "เงา", "เสียง", "ทำไม")):
            opening_note = "Prioritize the strongest existing hook signal; do not add exposition before it."
        else:
            opening_note = "Create an immediate visual/action/question hook without inventing unsupported facts."
        stage = "GRAB 0–3s → QUESTION 3–8s → PULL 8–15s"
    else:
        opening_note = "Do not repeat the opening hook. Advance the story."
        stage = "STORY FLOW"
    return "\n".join([
        HOOK_PACING_MASTER,
        "SCENE PACING DIRECTIVE",
        f"Scene: {scene.get('id', 'UNKNOWN')} ({scene_index + 1}/{total})",
        f"Opening: {opening}",
        f"Hook/Pacing stage: {stage}",
        opening_note,
        "DRAMATIC CHANGE TEST: State what meaningfully changes from scene start to end.",
        "If nothing changes, SHORTEN/MERGE/REMOVE unless intentional stillness itself builds tension or emotion.",
        "ANTI-FILLER TEST: identify redundant exposition, walking, looking, generic establishing footage, repeated reactions, dialogue or transitions.",
        "PACING DECISION: choose KEEP / SHORTEN / MERGE / REMOVE / HOLD and give the dramatic reason.",
        "TIMING: do not force equal-length shots. Cut when thought/action/reaction is complete; preserve meaningful silence.",
        "CONTINUITY: preserve blocking, eyelines, emotional state, lighting, sound and visual locks while removing only unnecessary material.",
    ])


def build_hook_3_stage_plan(episode: dict) -> dict[str, Any]:
    scenes = episode.get("scenes", [])
    if not scenes:
        return {"stages": [], "issues": ["No scenes available for hook analysis"], "score": 0}
    text = _text(scenes[0], "title", "action", "narration", "dialogue", "story_purpose", "conflict", "reveal", "story_question")
    stages = [
        {"stage": "GRAB", "window": "0–3s", "goal": "Immediate curiosity/danger/mystery/emotional shock"},
        {"stage": "QUESTION", "window": "3–8s", "goal": "Specific unanswered question"},
        {"stage": "PULL", "window": "8–15s", "goal": "Consequence/threat/discovery/clue that demands the next beat"},
    ]
    issues: list[str] = []
    if not _has(text, ("danger", "threat", "mystery", "secret", "shadow", "voice", "impossible", "อันตราย", "ภัย", "ลึกลับ", "ความลับ", "เงา", "เสียง", "ทำไม", "เกิดอะไร")):
        issues.append("GRAB: no strong curiosity/danger/mystery signal detected")
    if not _has(text, ("?", "why", "what", "who", "how", "ทำไม", "อะไร", "ใคร", "อย่างไร", "ปริศนา", "คำถาม")):
        issues.append("QUESTION: no explicit unanswered-question signal detected")
    if not _has(text, ("threat", "danger", "consequence", "discover", "reveal", "clue", "choice", "escape", "อันตราย", "ผลลัพธ์", "ค้นพบ", "เปิดเผย", "เบาะแส", "ทางเลือก", "หนี")):
        issues.append("PULL: no consequence/threat/discovery/clue signal detected")
    return {"stages": stages, "issues": issues, "score": max(0, 100 - len(issues) * 20)}


def pacing_structure_report(episode: dict) -> dict[str, Any]:
    scenes = episode.get("scenes", [])
    if not scenes:
        return {"score": 0, "issues": ["No scenes available for pacing analysis"], "scene_decisions": []}
    issues: list[str] = []
    decisions: list[dict[str, str]] = []
    for i, scene in enumerate(scenes):
        text = _text(scene, "action", "narration", "story_purpose", "conflict", "reveal", "payoff", "emotional_beat")
        meaningful = bool(_text(scene, "story_purpose", "conflict", "reveal", "payoff", "action"))
        stillness = _has(text, ("tension", "anticipation", "silence", "grief", "fear", "suspense", "เงียบ", "ตึงเครียด", "รอ", "หวาดกลัว"))
        repetitive = _has(text, ("again", "repeat", "repeated", "เดินต่อ", "มอง", "เดิน", "ซ้ำ"))
        if not meaningful and not stillness:
            decision = "SHORTEN/REMOVE"
            issues.append(f"{scene.get('id', i + 1)}: no clear dramatic change or meaningful stillness")
        elif repetitive and not stillness:
            decision = "SHORTEN/MERGE"
            issues.append(f"{scene.get('id', i + 1)}: possible repetitive action/transition")
        else:
            decision = "KEEP"
        decisions.append({"scene_id": str(scene.get("id", i + 1)), "decision": decision})
    return {"score": max(0, 100 - len(issues) * 15), "issues": issues, "scene_decisions": decisions}
