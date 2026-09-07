from __future__ import annotations

import argparse
import os
from pathlib import Path

import yaml
from google import genai
from google.genai import types


def generate_image(client: genai.Client, prompt: str, out: Path) -> None:
    if out.exists() and out.stat().st_size > 0:
        print(f"Reuse reference: {out}")
        return
    response = client.models.generate_content(
        model=os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image"),
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            response_format={"image": {"aspect_ratio": "16:9", "image_size": "2K"}},
        ),
    )
    for part in response.parts:
        if part.inline_data is not None:
            image = part.as_image()
            out.parent.mkdir(parents=True, exist_ok=True)
            image.save(out)
            print(f"Generated reference: {out}")
            return
    raise RuntimeError(f"Gemini image generation returned no image for {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate persistent character/environment references for Veo.")
    parser.add_argument("episode")
    parser.add_argument("out_dir")
    parser.add_argument("--scene", default=None)
    args = parser.parse_args()

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is required for reference asset generation.")

    episode = yaml.safe_load(Path(args.episode).read_text(encoding="utf-8"))
    scenes = episode.get("scenes", [])
    if args.scene:
        scenes = [s for s in scenes if s["id"] == args.scene]
    if not scenes:
        raise ValueError("No scene available for reference generation")

    scene = scenes[0]
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    out = Path(args.out_dir)

    environment_prompt = (
        "Create a cinematic environment reference image for an AI drama. "
        f"EXACT LOCATION: {scene.get('location', '')}. EXACT TIME: {scene.get('time', '')}. "
        f"ACTION CONTEXT: {scene.get('action', '')}. "
        "Show the stable physical architecture, furniture, doors, windows, signs and spatial layout. "
        "No characters, no text, no watermark. This image is a continuity anchor: do not redesign the environment."
    )
    generate_image(client, environment_prompt, out / "environment.png")

    for character in episode.get("characters", []):
        cid = character.get("id", "character")
        prompt = (
            "Create a neutral cinematic character reference portrait for continuity in an AI drama. "
            f"CHARACTER ID: {cid}. NAME: {character.get('name', '')}. "
            f"ROLE: {character.get('role', '')}. APPEARANCE: {character.get('appearance', '')}. "
            f"PERSONALITY: {character.get('personality', '')}. "
            f"CONTINUITY NOTES: {character.get('continuity_notes', '')}. "
            "Preserve face, age, hair, eye color, body proportions and wardrobe exactly as described. "
            "Neutral expression, front/three-quarter cinematic portrait, plain background, no text."
        )
        generate_image(client, prompt, out / f"{cid}.png")

    print(f"Reference assets ready: {out}")


if __name__ == "__main__":
    main()
