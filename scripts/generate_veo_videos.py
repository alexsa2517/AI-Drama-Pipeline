from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image


def load_reference(path: Path):
    return Image.open(path) if path.exists() else None


def generate_one(client: genai.Client, model: str, prompt: str, out: Path, aspect_ratio: str, references: list[Image.Image]) -> None:
    ref_images = [types.VideoGenerationReferenceImage(image=image, reference_type="asset") for image in references[:3]]
    config = types.GenerateVideosConfig(number_of_videos=1, aspect_ratio=aspect_ratio, duration_seconds=os.getenv("VEO_DURATION_SECONDS", "8"))
    if ref_images:
        config.reference_images = ref_images
    operation = client.models.generate_videos(model=model, prompt=prompt, config=config)
    while not operation.done:
        print(f"Waiting for Veo: {out.name}")
        time.sleep(10)
        operation = client.operations.get(operation)
    generated = operation.response.generated_videos[0]
    out.parent.mkdir(parents=True, exist_ok=True)
    client.files.download(file=generated.video, destination=str(out))
    print(f"Generated: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate speaker/reaction Veo clips from the AI Drama shot manifest.")
    parser.add_argument("shot_manifest")
    parser.add_argument("video_dir")
    parser.add_argument("--reaction-dir", default="inputs/two_character_reactions")
    parser.add_argument("--references", default="outputs/references")
    parser.add_argument("--model", default=os.getenv("VEO_MODEL", "veo-3.1-generate-preview"))
    parser.add_argument("--aspect-ratio", default=os.getenv("VEO_ASPECT_RATIO", "9:16"))
    parser.add_argument("--scene", default=None)
    args = parser.parse_args()

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is required for automatic Veo generation.")

    payload = json.loads(Path(args.shot_manifest).read_text(encoding="utf-8"))
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    out_dir = Path(args.video_dir)
    reaction_dir = Path(args.reaction_dir)
    refs = Path(args.references)
    environment = load_reference(refs / "environment.png")
    out_dir.mkdir(parents=True, exist_ok=True)
    reaction_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    video_manifest = []
    for item in payload.get("shots", []):
        scene_id = item["scene_id"]
        if args.scene and scene_id != args.scene:
            continue
        shot = item.get("shot", {})
        turn = shot.get("dialogue_turn")
        if turn is None:
            continue
        shot_type = str(shot.get("type", "")).lower()
        purpose = str(shot.get("purpose", "")).lower()
        is_reaction = "reaction" in shot_type or "reaction" in purpose
        subject = shot.get("subject", "active speaker")
        character_ref = load_reference(refs / f"{subject}.png")
        listener = next((c.get("id") for c in item.get("characters", []) if c.get("id") != subject), None)
        listener_ref = load_reference(refs / f"{listener}.png") if listener else None

        if is_reaction:
            output = reaction_dir / f"turn{turn}_{subject}.mp4"
            role_instruction = f"REACTION SHOT: {subject} is the silent listener. Do not move the mouth or speak. Use natural blinking, gaze toward the active speaker, breathing and subtle facial reaction."
        else:
            output = out_dir / f"turn{turn}_{subject}.mp4"
            role_instruction = f"ACTIVE SPEAKER: {subject}. Keep the face clearly visible for later lip-sync. Do not make the silent listener speak or move their mouth."

        if output.exists() and output.stat().st_size > 0:
            print(f"Reuse: {output}")
            video_manifest.append({"scene_id": scene_id, "turn": turn, "subject": subject, "role": "reaction" if is_reaction else "speaker", "file": str(output)})
            continue

        direction = item.get("gemini_flash", {})
        prompt = "\n\n".join([
            "CINEMATIC AI DRAMA VIDEO SHOT",
            item.get("video_prompt", ""),
            direction.get("camera_instruction", ""),
            direction.get("speaker_instruction", ""),
            direction.get("listener_instruction", ""),
            role_instruction,
            "Use the supplied reference images as hard continuity anchors.",
            "The environment reference is authoritative: remain inside that exact physical location.",
            "Do not relocate the scene, redesign architecture, change furniture, alter wardrobe, or invent characters.",
            "Camera movement is allowed only within the same physical environment.",
            "Do not invent dialogue. Thai dialogue will be applied separately during lip-sync.",
        ])
        references = [r for r in [environment, character_ref, listener_ref] if r is not None]
        generate_one(client, args.model, prompt, output, args.aspect_ratio, references)
        generated += 1
        video_manifest.append({"scene_id": scene_id, "turn": turn, "subject": subject, "role": "reaction" if is_reaction else "speaker", "file": str(output)})

    manifest_path = Path("outputs/automation/video_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(video_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Veo generation complete: {generated} new clips")
    print(f"Video manifest: {manifest_path}")


if __name__ == "__main__":
    main()
