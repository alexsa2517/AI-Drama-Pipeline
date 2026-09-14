# AI Drama Pipeline

**V1 — Prompt + Dialogue Production Pipeline**

AI-assisted production pipeline for short-form dramatic stories. The pipeline converts a structured episode YAML into production-ready story, image, video, voice and dialogue-production manifests.

## Pipeline

`Concept → Legend Research → Hook → Beginning → Middle → Climax/Ending → Character Bible → Scene Visual Lock → Feature-Film Cinema → Feature-Film Sound → Image → Video → Character Voice → Lip-Sync → QA`

## Feature-Film Legend Story Structure

For legends, folklore and mythology, the pipeline now applies a dedicated story engine before scene production:

- **Hook — first 1–3 seconds:** immediate mystery, danger, contradiction, impossible image or emotional question.
- **Beginning:** establish protagonist, world, desire/problem and inciting incident.
- **Middle:** escalate conflict, reveal clues, deepen relationships, force choices and close escape routes.
- **Ending:** climax, reveal, consequence, emotional reaction and payoff.
- **Causality:** each scene must create a meaningful reason for the next scene to exist.
- **Foreshadowing / payoff:** visual, dialogue and story seeds can be planted early and paid off later.
- **Legend integrity:** separate historical fact, traditional legend, interpretation and fictionalized dramatization.

Legend episodes receive a `story_blueprint.md` plus per-scene story direction. Existing scene YAML remains compatible; optional fields such as `story_purpose`, `conflict`, `emotional_beat`, `reveal`, `story_question`, `foreshadowing` and `payoff` can make the story direction more explicit.

## Quick Start

```bash
python -m pip install -r requirements.txt
python scripts/generate_episode.py examples/episode-001/episode.yaml
```

For dialogue scenes, generate voice manifests:

```bash
python scripts/generate_dialogue_manifest.py examples/episode-001/episode.yaml
```

Each dialogue manifest binds the exact dialogue to its `CHARACTER ID`, preserves the Thai language/emotion/delivery, and declares generated audio as the authoritative timing source.

After a scene video and character dialogue audio have been generated, run Wav2Lip:

```bash
python scripts/run_wav2lip.py \
  --video outputs/video/SC001.mp4 \
  --audio outputs/voice/audio/SC001.wav \
  --checkpoint /path/to/wav2lip_gan.pth \
  --wav2lip-dir /path/to/Wav2Lip \
  --out outputs/final/SC001-lipsync.mp4
```

The image/video prompt pack also contains a **HARD SCENE VISUAL LOCK**. Camera angles may change, but the physical environment must remain the same unless the script explicitly changes location.

## Output

```text
output/episode-001/
├── story.md
├── story_blueprint.md       # legends / folklore / mythology
├── production.json
└── scenes/
    ├── SC001-image.md
    ├── SC001-video.md
    ├── SC001-voice.md
    ├── SC002-image.md
    ├── SC002-video.md
    └── SC002-voice.md

outputs/voice/
├── manifest.json
├── SC001.json
└── SC002.json
```

## Dialogue Rules

- `CHARACTER ID` owns the voice identity.
- The supplied dialogue must be spoken exactly; no invented words.
- The generated audio duration is the authoritative timing for lip-sync.
- Only the active speaker moves their mouth; listeners remain silent.
- Thai lip-sync must follow the actual generated audio.
- Natural blinking, gaze shifts, breathing and micro-expressions are required.
- Face, eyes, hair, wardrobe and body proportions remain consistent across shots.
- Scene location remains locked while camera coverage changes.
- Silence is allowed; music must never cover important dialogue.

## Design Principles

- **Character continuity first** — identity and wardrobe notes are preserved across scenes.
- **Story continuity first** — every scene has a dramatic purpose and causal connection.
- **Scene-first production** — every scene has independent image, video and voice outputs.
- **Feature-film direction** — cinematography, acting, sound and story structure are generated as coordinated layers.
- **Provider-agnostic** — voice/video providers can be swapped without changing episode data.
- **Human review** — generated assets are reviewed before publishing.
- **Reusable data** — episode YAML is the single source of truth.

## Current Scope

- Episode data model
- Validation
- Legend fact-first research guardrails
- Feature-film story structure
- Hook / beginning / middle / ending direction
- Story causality and payoff guidance
- Hard scene visual lock
- Feature-film cinematography direction
- Feature-film sound design
- Character animation/lip-sync rules
- Dialogue timing
- Adaptive music direction
- Per-scene voice manifests
- Wav2Lip execution wrapper
- Automated tests for continuity and dialogue manifests

> The system does not auto-publish content.
