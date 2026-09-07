# AI Drama Pipeline

AI-assisted pipeline for producing short-form dramatic stories from concept to production-ready prompts.

## V1 Goals

- Story and episode planning
- Scene breakdown
- Character Bible
- Image-generation prompts
- Video-generation prompts
- Narration / voice prompts
- Production status tracking
- Provider-agnostic prompt templates

## Pipeline

`Concept → Story → Characters → Scenes → Image Prompts → Video Prompts → Voice → Export`

## Project Structure

```text
AI-Drama-Pipeline/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── architecture.md
│   └── workflow.md
├── config/
│   └── pipeline.yaml
├── schemas/
│   ├── episode.schema.json
│   ├── character.schema.json
│   └── scene.schema.json
├── prompts/
│   ├── story.md
│   ├── character-bible.md
│   ├── image.md
│   ├── video.md
│   └── voice.md
├── examples/
│   └── episode-001/
│       ├── episode.yaml
│       └── scenes/
└── src/
    └── README.md
```

## Status

V1 foundation — schema-first, provider-agnostic, ready for implementation.
