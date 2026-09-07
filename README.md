# AI Drama Pipeline

**V1 — Prompt + Dialogue Production Pipeline**

AI-assisted production pipeline for short-form dramatic stories. The pipeline converts a structured episode YAML into production-ready story, image, video, voice and dialogue-production manifests.

## Pipeline

`Concept → Episode → Character Bible → Scene Visual Lock → Image → Base Video → Character Voice → Lip-Sync → QA`

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
- **Scene-first production** — every scene has independent image, video and voice outputs.
- **Provider-agnostic** — voice/video providers can be swapped without changing episode data.
- **Human review** — generated assets are reviewed before publishing.
- **Reusable data** — episode YAML is the single source of truth.

## Current Scope

- Episode data model
- Validation
- Prompt generation
- Hard scene visual lock
- Character animation/lip-sync rules
- Dialogue timing
- Adaptive music direction
- Per-scene voice manifests
- Wav2Lip execution wrapper
- Automated tests for continuity and dialogue manifests

> The system does not auto-publish content.
