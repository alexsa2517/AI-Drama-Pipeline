from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from google import genai
from google.genai import types


def call_director(client: genai.Client, episode: dict, shot: dict) -> dict:
    prompt = f"""
You are the senior continuity director for an AI cinematic drama pipeline.
Model role: planning/directing only. Do NOT invent locations, characters, dialogue, props or story facts.

EPISODE:
{json.dumps(episode, ensure_ascii=False, indent=2)}

SHOT:
{json.dumps(shot, ensure_ascii=False, indent=2)}

Return JSON with exactly these keys:
- video_prompt: a production-ready cinematic prompt for Veo 3.1
- continuity_checks: array of short hard constraints
- camera_instruction: concise camera direction
- speaker_instruction: concise instruction identifying who may move their mouth
- listener_instruction: concise silent reaction direction
- music_direction: concise scene-specific music/silence direction

HARD RULES:
1. The current scene location is immutable unless the script explicitly changes location.
2. Camera changes may reveal different views, but never change the physical environment.
3. Preserve architecture, furniture, doors, windows, signs, lighting, wardrobe and spatial blocking.
4. Preserve character identity, face, hair, age, proportions and wardrobe.
5. Only the active speaker moves their mouth. A listener must remain silent.
6. Never invent dialogue. The supplied dialogue is authoritative.
7. Keep cinematic movement subtle and physically plausible.
8. This is one continuous scene, not a montage of unrelated locations.
9. Output valid JSON only.
"""
    response = client.models.generate_content(
        model=os.getenv("GEMINI_FLASH_MODEL", "gemini-3.8-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    text = response.text or "{}"
    return json.loads(text)


def _shot_label(shot: object) -> str:
    """Return a readable shot label for both legacy string and richer dict plans."""
    if isinstance(shot, dict):
        return str(shot.get("shot", shot.get("type", "unknown")))
    return str(shot)


def main() -> None:
    parser = argparse.ArgumentParser(description="Use Gemini Flash as the automated AI Drama director.")
    parser.add_argument("shot_manifest")
    parser.add_argument("episode")
    parser.add_argument("out")
    parser.add_argument("--scene", default=None)
    args = parser.parse_args()

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is required for Gemini Flash director stage.")

    manifest = json.loads(Path(args.shot_manifest).read_text(encoding="utf-8"))
    episode = __import__("yaml").safe_load(Path(args.episode).read_text(encoding="utf-8"))
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    for item in manifest.get("shots", []):
        if args.scene and item.get("scene_id") != args.scene:
            continue
        print(f"Gemini Flash directing shot {_shot_label(item.get('shot'))}")
        direction = call_director(client, episode, item)
        item["gemini_flash"] = direction
        if direction.get("video_prompt"):
            item["video_prompt"] = direction["video_prompt"]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gemini Flash manifest: {out}")


if __name__ == "__main__":
    main()
