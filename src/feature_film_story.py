from __future__ import annotations

from typing import Any


LEGEND_STORY_MASTER = """FEATURE-FILM LEGEND STORY ENGINE

Purpose: turn a legend into a dramatic, emotionally escalating story rather than a sequence of disconnected scenes.

HOOK — FIRST 1–3 SECONDS
- Open on the most intriguing, dangerous, mysterious or emotionally charged moment available.
- Create an immediate unanswered question, contradiction, threat, impossible image or forbidden secret.
- Do not spend the opening on generic landscape, exposition or greetings unless the calm itself creates tension.
- The hook must make the audience need the next beat.

BEGINNING — SETUP + INCITING INCIDENT
- Establish who matters, where we are, what the world believes and what feels wrong.
- Introduce the protagonist's immediate desire or problem.
- Deliver the inciting incident early enough to change the direction of the story.
- Seed a mystery, promise, symbol, object, warning or relationship that can pay off later.

MIDDLE — ESCALATION + DISCOVERY
- Every scene must change the situation: reveal information, increase danger, deepen a relationship, create a harder choice or close an escape route.
- Escalate stakes rather than repeating the same discovery.
- Use reversals, complications, clues, false assumptions and meaningful reactions.
- Reveal the legend progressively; protect the strongest reveal until the story has earned it.
- Dialogue should carry intention and subtext, not merely explain the plot.

ENDING — CLIMAX + REVEAL + PAYOFF
- Resolve the central dramatic question or deliberately transform it.
- Pay off important visual, dialogue and story seeds planted earlier.
- Give the protagonist a consequence, choice, realization, sacrifice, victory, loss or transformation.
- End with a memorable final image, line, reveal or emotional aftertaste.
- Do not rush the final reveal; allow a reaction beat before the ending.

CAUSALITY RULE
- Scene N must create pressure, information or consequence that makes Scene N+1 necessary.
- Avoid scenes that could be removed without changing the story.

LEGEND INTEGRITY
- Preserve the distinction between sourced history, traditional legend, interpretation and fictionalized dramatization.
- Never invent historical evidence to make the drama work.
- Fictional dialogue and cinematic staging are allowed when clearly treated as dramatization.
"""


def _scene_count(episode: dict) -> int:
    return len(episode.get("scenes", []))


def _phase(index: int, total: int) -> str:
    if total <= 1:
        return "HOOK + CLIMAX"
    ratio = index / max(total - 1, 1)
    if index == 0:
        return "HOOK / OPENING"
    if ratio < 0.30:
        return "BEGINNING / SETUP + INCITING INCIDENT"
    if ratio < 0.75:
        return "MIDDLE / ESCALATION + DISCOVERY"
    if index == total - 1:
        return "ENDING / CLIMAX + PAYOFF"
    return "LATE MIDDLE / ESCALATION + APPROACH TO CLIMAX"


def build_legend_story_prompt(episode: dict) -> str:
    scenes = episode.get("scenes", [])
    total = len(scenes)
    title = str(episode.get("title", "Untitled Legend"))
    logline = str(episode.get("logline", ""))
    genre = str(episode.get("genre", "legend"))
    country = str(episode.get("country", episode.get("region", "")))

    lines = [
        LEGEND_STORY_MASTER,
        "STORY BLUEPRINT",
        f"Title: {title}",
        f"Genre: {genre}",
        f"Country/region: {country or 'not specified'}",
        f"Logline: {logline}",
        f"Scene count: {total}",
        "",
        "GLOBAL DRAMATIC QUESTIONS",
        "- What does the audience want to know immediately?",
        "- What does the protagonist want, and what prevents it?",
        "- What is the central mystery or supernatural promise?",
        "- What is at stake if the protagonist fails?",
        "- What must be paid off by the ending?",
    ]

    if scenes:
        lines.extend(["", "SCENE-BY-SCENE STORY FUNCTION"])
        for index, scene in enumerate(scenes):
            phase = _phase(index, total)
            lines.extend([
                f"SCENE {index + 1} / {scene.get('id', 'UNKNOWN')} — {phase}",
                f"Purpose: {scene.get('story_purpose', 'Must advance the story; do not allow a static scene.')}",
                f"Action: {scene.get('action', '')}",
                f"Conflict: {scene.get('conflict', 'Introduce or escalate a meaningful obstacle.')}",
                f"Emotional beat: {scene.get('emotional_beat', scene.get('emotion', 'natural'))}",
                f"Reveal/question: {scene.get('reveal', scene.get('story_question', 'Create or deepen an unanswered question.'))}",
                f"Payoff/seed: {scene.get('payoff', scene.get('foreshadowing', 'Plant or advance a setup that matters later.'))}",
                "Transition rule: the result of this scene must create a reason for the next scene to exist.",
            ])

    lines.extend([
        "",
        "HOOK REQUIREMENT",
        "The first visual/audio beat must create curiosity, danger, mystery or emotional shock within approximately 1–3 seconds.",
        "",
        "ENDING REQUIREMENT",
        "The final scene must answer, transform or deliberately deepen the central question and provide a satisfying final beat.",
    ])
    return "\n".join(lines)


def build_scene_story_prompt(episode: dict, scene: dict, index: int) -> str:
    total = _scene_count(episode)
    phase = _phase(index, total)
    purpose = scene.get("story_purpose", "Advance the story with a meaningful change.")
    conflict = scene.get("conflict", "Create or escalate an obstacle.")
    emotional = scene.get("emotional_beat", scene.get("emotion", "natural"))
    reveal = scene.get("reveal", scene.get("story_question", "Deepen an unanswered question."))
    payoff = scene.get("payoff", scene.get("foreshadowing", "Plant or advance a future payoff."))
    return "\n".join([
        "FEATURE-FILM STORY DIRECTION",
        f"Story phase: {phase}",
        f"Scene position: {index + 1}/{total}",
        f"Scene purpose: {purpose}",
        f"Conflict / pressure: {conflict}",
        f"Emotional beat: {emotional}",
        f"Mystery / reveal: {reveal}",
        f"Foreshadowing / payoff: {payoff}",
        "Causality: this scene must cause a meaningful change that justifies the next scene.",
        "Do not dump exposition. Prefer visual action, behavior, subtext, reaction and discovery.",
        "For the opening scene, hook the audience immediately; for the final scene, prioritize climax, reaction and payoff.",
    ])
