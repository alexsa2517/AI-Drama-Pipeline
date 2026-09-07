from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from src.voice_pipeline import build_tts_instruction, build_voice_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate per-scene Thai TTS manifests.")
    parser.add_argument("episode", help="Path to episode YAML")
    parser.add_argument("--out", default="outputs/voice", help="Output directory")
    args = parser.parse_args()

    episode = yaml.safe_load(Path(args.episode).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    manifests = []
    for scene in episode.get("scenes", []):
        manifest = build_voice_manifest(episode, scene, str(out / "audio"))
        manifest["tts_instruction"] = build_tts_instruction(manifest)
        manifests.append(manifest)
        (out / f"{scene['id']}.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    (out / "manifest.json").write_text(
        json.dumps(manifests, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Generated {len(manifests)} dialogue manifests in {out}")


if __name__ == "__main__":
    main()
