from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.speech_pipeline import build_dialogue_video_prompt


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a talking-character video prompt")
    parser.add_argument("episode", help="Path to episode.yaml")
    parser.add_argument("scene_id", help="Scene ID, e.g. SC001")
    args = parser.parse_args()

    with open(args.episode, "r", encoding="utf-8") as f:
        episode = yaml.safe_load(f)

    scene = next((s for s in episode.get("scenes", []) if s.get("id") == args.scene_id), None)
    if scene is None:
        raise SystemExit(f"Scene not found: {args.scene_id}")

    prompt = build_dialogue_video_prompt(episode, scene)
    if not prompt:
        raise SystemExit("This scene has no dialogue. Add speaker and dialogue fields to episode.yaml.")

    print(prompt)


if __name__ == "__main__":
    main()
