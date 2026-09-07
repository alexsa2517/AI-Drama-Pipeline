# AI Drama Pipeline

**V1 — Prompt Pack Generator**

AI-assisted production pipeline for short-form dramatic stories. V1 converts a structured episode YAML into production-ready story, image, video and narration prompts.

## Pipeline

`Concept → Episode → Character Bible → Scenes → Image → Video → Voice → Production Manifest`

## Quick Start

```bash
python -m pip install -r requirements.txt
python scripts/generate_episode.py examples/episode-001/episode.yaml
```

Output:

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
```

## Design Principles

- **Character continuity first** — identity and wardrobe notes are preserved across scenes.
- **Scene-first production** — every scene has independent image, video and voice outputs.
- **Provider-agnostic** — prompts are not locked to a single image/video model.
- **Human review** — generated prompts are drafts for production review, not automatic publishing.
- **Reusable data** — episode YAML becomes the single source of truth.

## V1 Scope

- Episode data model
- Validation
- Prompt generation
- CLI generation
- Example episode
- Production manifest

## Roadmap

### V1.1

- Stronger character continuity injection
- Hook scoring
- Scene continuity validation
- Prompt quality checks

### V2

- LLM provider adapters
- Automatic script generation
- Character Bible generation
- Batch episode generation
- Prompt pack export

### V3

- Image/video provider integrations
- Asset tracking
- Production dashboard
- Automated QA
- CapCut-ready production metadata

> The system deliberately does not auto-publish content in V1.
