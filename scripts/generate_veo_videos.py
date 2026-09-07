from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from google import genai
from google.genai import types


def generate_one(client: genai.Client, model: str, prompt: str, out: Path, aspect_ratio: str) -> None:
    operation = client.models.generate_videos(
        model=model,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            number_of_videos=1,
            aspect_ratio=aspect_ratio,
        ),
    )
    while not operation.done:
        print(f"Waiting for Veo: {out.name}")
        time.sleep(10)
        operation = client.operations.get(operation)
    generated = operation.response.generated_videos[0]
    out.parent.mkdir(parents=True, exist_ok=True)
    client.files.download(file=generated.video, destination=str(out))
    print(f"Generated: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate speaker-specific Veo clips from the AI Drama shot manifest.")
    parser.add_argument("shot_manifest")
    parser.add_argument("video_dir")
    parser.add_argument("--model", default=os.getenv("VEO_MODEL", "veo-3.1-generate-preview"))
    parser.add_argument("--aspect-ratio", default=os.getenv("VEO_ASPECT_RATIO", "9:16"))
    parser.add_argument("--scene", default=None)
    args = parser.parse_args()

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is required for automatic Veo generation.")

    payload = json.loads(Path(args.shot_manifest).read_text(encoding="utf-8"))
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    out_dir = Path(args.video_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Generate one active-speaker clip per dialogue turn. Veo clips are 4/6/8 seconds;
    # the downstream renderer trims/concatenates them against the authoritative audio timeline.
    generated = 0
    for item in payload.get("shots", []):
        scene_id = item["scene_id"]
        if args.scene and scene_id != args.scene:
            continue
        shot = item.get("shot", {})
        turn = shot.get("dialogue_turn")
        subject = shot.get("subject", "active speaker")
        if turn is None:
            continue
        filename = f"turn{turn}_{subject}.mp4"
        output = out_dir / filename
        if output.exists() and output.stat().st_size > 0:
            print(f"Reuse: {output}")
            continue

        prompt = "\n\n".join([
            "CINEMATIC AI DRAMA VIDEO SHOT",
            item.get("video_prompt", ""),
            f"ACTIVE SPEAKER: {subject}",
            f"DIALOGUE TURN: {turn}",
            "Generate a speaker-focused shot. The active speaker is clearly visible and centered enough for later lip-sync.",
            "The listener, if visible, remains silent and only performs natural blinking, gaze and subtle reaction.",
            "Keep the exact same physical environment, architecture, furniture, lighting, wardrobe and character identity established by the scene.",
            "Do not relocate the scene. Camera changes are allowed only within the same physical environment.",
            "Do not invent new characters, locations, props or dialogue.",
        ])
        generate_one(client, args.model, prompt, output, args.aspect_ratio)
        generated += 1

    print(f"Veo generation complete: {generated} new clips")


if __name__ == "__main__":
    main()
