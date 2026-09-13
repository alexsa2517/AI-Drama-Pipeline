from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Allow direct execution from the repository root or from any working directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml
from gtts import gTTS

try:
    import edge_tts
except ImportError:  # pragma: no cover - dependency is declared in requirements.txt
    edge_tts = None

from src.dialogue_scene import normalize_dialogue

DEFAULT_EDGE_VOICES = {
    "female": "th-TH-PremwadeeNeural",
    "male": "th-TH-NiwatNeural",
}


def resolve_provider(voice: dict) -> str:
    provider = str(voice.get("provider", "edge-tts")).strip().lower().replace("_", "-")
    if provider in {"edge", "edge-tts", "edgetts"}:
        return "edge-tts"
    if provider in {"gtts", "google-tts"}:
        return "gtts"
    raise ValueError(f"Unsupported TTS provider: {provider}")


def resolve_edge_voice(voice: dict) -> str:
    explicit = str(voice.get("voice", "")).strip()
    if explicit:
        return explicit
    gender = str(voice.get("gender", "female")).strip().lower()
    return DEFAULT_EDGE_VOICES.get(gender, DEFAULT_EDGE_VOICES["female"])


async def save_edge_tts(text: str, path: Path, voice: dict) -> None:
    if edge_tts is None:
        raise RuntimeError("edge-tts is not installed. Run: pip install edge-tts")

    communicator = edge_tts.Communicate(
        text=text,
        voice=resolve_edge_voice(voice),
        rate=str(voice.get("rate", "+0%")),
        volume=str(voice.get("volume", "+0%")),
        pitch=str(voice.get("pitch", "+0Hz")),
    )
    await communicator.save(str(path))


def generate_audio(text: str, path: Path, voice: dict, episode_language: str) -> tuple[str, str]:
    provider = resolve_provider(voice)
    if provider == "edge-tts":
        asyncio.run(save_edge_tts(text, path, voice))
        return provider, resolve_edge_voice(voice)

    lang = voice.get("language", episode_language)
    gTTS(text=text, lang=lang, slow=bool(voice.get("slow", False))).save(str(path))
    return provider, str(lang)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate real character speech per dialogue turn for deterministic lip-sync."
    )
    parser.add_argument("episode")
    parser.add_argument("--scene", default=None)
    parser.add_argument("--out", default="outputs/two_character_audio")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate audio even when an existing track is present.",
    )
    args = parser.parse_args()

    episode = yaml.safe_load(Path(args.episode).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []

    for scene in episode.get("scenes", []):
        if args.scene and scene["id"] != args.scene:
            continue
        for turn in normalize_dialogue(scene):
            speaker = turn["speaker"]
            text = turn["dialogue"]
            path = out / f"{scene['id']}_turn{turn['turn']}_{speaker}.mp3"
            voice = next(
                (c.get("voice", {}) for c in episode.get("characters", []) if c.get("id") == speaker),
                {},
            )

            if not path.exists() or path.stat().st_size == 0 or args.force:
                provider, resolved_voice = generate_audio(
                    text=text,
                    path=path,
                    voice=voice,
                    episode_language=episode.get("language", "th"),
                )
                print(f"Generated {speaker} turn {turn['turn']}: {resolved_voice} -> {path}")
            else:
                provider = resolve_provider(voice)
                resolved_voice = resolve_edge_voice(voice) if provider == "edge-tts" else str(voice.get("language", episode.get("language", "th")))
                print(f"Reuse {path}")

            results.append({
                "scene_id": scene["id"],
                "turn": turn["turn"],
                "speaker": speaker,
                "dialogue": text,
                "audio": str(path),
                "provider": provider,
                "voice": resolved_voice,
                "pause_after": float(turn.get("pause_after", 0.25)),
                "emotion": turn.get("emotion", "natural"),
                "delivery": turn.get("delivery", "natural conversational delivery"),
            })

    manifest = out / "manifest.json"
    manifest.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(results)} dialogue tracks: {manifest}")


if __name__ == "__main__":
    main()
