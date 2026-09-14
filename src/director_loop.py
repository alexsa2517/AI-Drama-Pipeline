from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable


DIRECTOR_LOOP_MASTER = """AUTONOMOUS DIRECTOR LOOP

DIRECTOR → RENDER → WATCH/EVALUATE → DECIDE → REVISE → RENDER AGAIN

The director owns the quality gate. A render is never automatically final.
Evaluate the actual generated result when observations or machine vision/audio metrics are available.
Revise only the smallest failing unit and preserve all locked elements.
Never regenerate a good shot merely because another shot failed.
"""


STATES = (
    "DIRECT",
    "RENDER",
    "EVALUATE",
    "DECIDE",
    "REVISE",
    "FINAL",
    "BLOCKED",
)


@dataclass
class DirectorLoopState:
    episode_id: str
    scene_id: str
    iteration: int = 0
    max_iterations: int = 3
    status: str = "DIRECT"
    shot_results: list[dict[str, Any]] = field(default_factory=list)
    locked: dict[str, Any] = field(default_factory=dict)
    issues: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)


def _score(value: Any, default: float = 100.0) -> float:
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return default


def evaluate_render(
    render_result: dict[str, Any] | None,
    observations: Iterable[dict[str, Any]] | None = None,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Normalize machine/human render observations into director evidence."""
    thresholds = thresholds or {
        "identity": 85.0,
        "continuity": 85.0,
        "eyeline": 90.0,
        "motion": 80.0,
        "cinematography": 80.0,
        "lighting": 80.0,
        "audio": 80.0,
        "lip_sync": 85.0,
    }
    evidence = dict(render_result or {})
    evidence.setdefault("status", "rendered")
    issues: list[dict[str, Any]] = []
    for obs in observations or []:
        evidence.update(obs)

    for key, threshold in thresholds.items():
        if key not in evidence:
            continue
        score = _score(evidence[key])
        if score < threshold:
            issues.append({"type": key, "score": score, "threshold": threshold})

    explicit = evidence.get("issues", [])
    for issue in explicit:
        if isinstance(issue, str):
            issues.append({"type": "observed", "message": issue})
        elif isinstance(issue, dict):
            issues.append(issue)

    return {
        "passed": not issues,
        "issues": issues,
        "evidence": evidence,
        "summary": "PASS" if not issues else f"FAIL: {len(issues)} issue(s)",
    }


def decide_revision(evaluation: dict[str, Any], locked: dict[str, Any] | None = None) -> dict[str, Any]:
    """Convert evaluation evidence into minimal, shot-local revision commands."""
    locked = locked or {}
    issues = evaluation.get("issues", [])
    actions: list[dict[str, Any]] = []
    for issue in issues:
        kind = str(issue.get("type", "observed"))
        message = str(issue.get("message", kind))
        if kind == "eyeline":
            action = "REVISE_EYELINE"
            preserve = ["character_identity", "dialogue_timing", "lighting", "wardrobe"]
        elif kind == "identity":
            action = "REVISE_IDENTITY_LOCK"
            preserve = ["story", "blocking", "camera_plan"]
        elif kind == "continuity":
            action = "REVISE_CONTINUITY"
            preserve = ["character_identity", "wardrobe", "props", "screen_direction"]
        elif kind == "motion":
            action = "REVISE_MOTION"
            preserve = ["camera", "lighting", "dialogue_timing", "identity"]
        elif kind == "cinematography":
            action = "REVISE_CAMERA"
            preserve = ["story", "identity", "acting", "sound"]
        elif kind == "lighting":
            action = "REVISE_LIGHTING"
            preserve = ["camera", "identity", "blocking", "sound"]
        elif kind in {"audio", "lip_sync"}:
            action = "REVISE_AUDIO"
            preserve = ["picture_lock", "camera", "lighting"]
        else:
            action = "REVIEW_SHOT"
            preserve = ["all_locked_elements"]
        actions.append({
            "action": action,
            "message": message,
            "preserve": preserve,
            "locked_context": locked,
            "scope": "smallest_failing_shot_or_layer",
        })

    return {
        "decision": "FINAL" if not actions else "REVISE",
        "actions": actions,
        "principle": "Fix the smallest failing unit; do not regenerate passing shots.",
    }


def build_director_loop_prompt(
    episode: dict[str, Any],
    scene: dict[str, Any],
    iteration: int = 0,
    evaluation: dict[str, Any] | None = None,
) -> str:
    """Prompt for an AI director to review an actual render and choose the next action."""
    evaluation = evaluation or {}
    issues = evaluation.get("issues", [])
    return "\n\n".join([
        DIRECTOR_LOOP_MASTER,
        f"Episode: {episode.get('id', '')}",
        f"Scene: {scene.get('id', '')}",
        f"Iteration: {iteration}",
        "CURRENT RENDER EVIDENCE",
        str(evaluation.get("evidence", "No render evidence supplied.")),
        "CURRENT ISSUES",
        str(issues or "None"),
        "DIRECTOR DECISION CONTRACT",
        "If the render passes: FINAL. Do not regenerate.",
        "If it fails: identify the smallest failing shot/layer and issue a surgical revision.",
        "Preserve character identity, visual style (including 3D), wardrobe, props, story beat, dialogue timing and all passing layers.",
        "If evidence is insufficient to judge a critical requirement: BLOCKED rather than pretending it passed.",
        "Never fix one issue by introducing a new continuity error.",
        "Output: FINAL or REVISE or BLOCKED, exact shot/layer, exact change, locked elements, acceptance criterion.",
    ])


def start_director_loop(episode: dict[str, Any], scene: dict[str, Any], max_iterations: int = 3) -> DirectorLoopState:
    return DirectorLoopState(
        episode_id=str(episode.get("id", "")),
        scene_id=str(scene.get("id", "")),
        max_iterations=max(1, int(max_iterations)),
        status="DIRECT",
    )


def record_render(state: DirectorLoopState, render_result: dict[str, Any]) -> DirectorLoopState:
    state.status = "EVALUATE"
    state.shot_results.append({"iteration": state.iteration, **render_result})
    return state


def review_and_decide(
    state: DirectorLoopState,
    render_result: dict[str, Any] | None = None,
    observations: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    evaluation = evaluate_render(render_result, observations)
    if evaluation["passed"]:
        state.status = "FINAL"
        state.issues = []
        state.decisions.append({"iteration": state.iteration, "decision": "FINAL"})
        return evaluation | {"decision": "FINAL"}

    if state.iteration >= state.max_iterations:
        state.status = "BLOCKED"
        state.issues = evaluation["issues"]
        state.decisions.append({"iteration": state.iteration, "decision": "BLOCKED", "reason": "max_iterations_reached"})
        return evaluation | {"decision": "BLOCKED", "reason": "max_iterations_reached"}

    decision = decide_revision(evaluation, state.locked)
    state.status = "REVISE"
    state.issues = evaluation["issues"]
    state.decisions.append({"iteration": state.iteration, **decision})
    return evaluation | decision


def apply_revision(state: DirectorLoopState, revision: dict[str, Any]) -> DirectorLoopState:
    """Advance one controlled revision without discarding prior good render evidence."""
    if revision.get("decision") != "REVISE":
        return state
    state.iteration += 1
    state.status = "RENDER"
    return state


def run_director_loop(
    episode: dict[str, Any],
    scene: dict[str, Any],
    render: Callable[[dict[str, Any], dict[str, Any], int, list[dict[str, Any]]], dict[str, Any]],
    observe: Callable[[dict[str, Any]], Iterable[dict[str, Any]]] | None = None,
    max_iterations: int = 3,
) -> DirectorLoopState:
    """Provider-agnostic orchestration. The existing renderer is injected; no provider is replaced."""
    state = start_director_loop(episode, scene, max_iterations)
    revision: list[dict[str, Any]] = []
    while state.iteration <= state.max_iterations:
        state.status = "RENDER"
        result = render(episode, scene, state.iteration, revision)
        state = record_render(state, result)
        observations = observe(result) if observe else None
        decision = review_and_decide(state, result, observations)
        if decision.get("decision") != "REVISE":
            break
        revision = decision.get("actions", [])
        state = apply_revision(state, decision)
    return state
