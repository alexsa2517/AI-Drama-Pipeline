from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml
from src.prompt_pack import build_scene_pack


def run(command: list[str]) -> None:
    print("$", " ".join(shlex.quote(x) for x in command))
    subprocess.run(command, cwd=ROOT, check=True)


def generate_shot_manifest(episode: dict, out: Path) -> Path:
    packs = build_scene_pack(episode)
    shots = []
    for pack in packs:
        scene = next(s for s in episode.get("scenes", []) if s["id"] == pack["scene_id"])
        for shot in pack.get("camera_plan", []):
            shots.append({
                "scene_id": scene["id"], "shot": shot,
                "location": scene.get("location", ""), "time": scene.get("time", ""),
                "visual_anchor": scene.get("visual_anchor", ""),
                "environment_lock": scene.get("environment_lock", ""),
                "characters": episode.get("characters", []),
                "image_prompt": pack["image"], "video_prompt": pack["video"],
                "dialogue": pack.get("dialogue", ""),
                "audio_direction": pack.get("audio_direction", ""),
            })
    payload = {
        "version": "3.0", "automation": "gemini-flash-plus-veo-one-command",
        "environment_policy": "same physical environment unless the script explicitly changes location",
        "speaker_policy": "only active speaker moves mouth; listener stays silent",
        "planning_model": os.getenv("GEMINI_FLASH_MODEL", "gemini-3.8-flash"),
        "video_model": os.getenv("VEO_MODEL", "veo-3.1-generate-preview"),
        "shots": shots,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="One-command AI Drama Pipeline: Gemini Flash director + reference images + Veo + lip-sync")
    parser.add_argument("episode")
    parser.add_argument("--scene", default=None)
    parser.add_argument("--audio-dir", default="outputs/two_character_audio")
    parser.add_argument("--video-dir", default="inputs/two_character_shots")
    parser.add_argument("--reaction-dir", default="inputs/two_character_reactions")
    parser.add_argument("--wav2lip-dir", default=os.getenv("WAV2LIP_DIR", "/content/Wav2Lip"))
    parser.add_argument("--checkpoint", default=os.getenv("WAV2LIP_CHECKPOINT", "/content/Wav2Lip/checkpoints/wav2lip_gan.pth"))
    parser.add_argument("--out", default="outputs/final/two_character_conversation.mp4")
    parser.add_argument("--skip-video-provider", action="store_true")
    args = parser.parse_args()

    episode_path = ROOT / args.episode
    episode = yaml.safe_load(episode_path.read_text(encoding="utf-8"))
    scenes = episode.get("scenes", [])
    if args.scene:
        scenes = [s for s in scenes if s["id"] == args.scene]
        if not scenes:
            raise ValueError(f"Scene not found: {args.scene}")
        episode = {**episode, "scenes": scenes}

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is required for Gemini Flash + Veo automation.")

    automation_dir = ROOT / "outputs" / "automation"
    shot_manifest = generate_shot_manifest(episode, automation_dir / "shot_manifest.json")
    print(f"[1/7] Shot manifest: {shot_manifest}")

    run([sys.executable, str(ROOT / "scripts" / "gemini_flash_director.py"), str(shot_manifest), str(episode_path), str(automation_dir / "gemini_shot_manifest.json"), *( ["--scene", args.scene] if args.scene else [] )])
    shot_manifest = automation_dir / "gemini_shot_manifest.json"
    print(f"[2/7] Gemini Flash director: {shot_manifest}")

    run([sys.executable, str(ROOT / "scripts" / "generate_reference_assets.py"), str(episode_path), str(ROOT / "outputs" / "references"), *( ["--scene", args.scene] if args.scene else [] )])
    print("[3/7] Character/environment references ready")

    run([sys.executable, str(ROOT / "scripts" / "generate_two_character_audio.py"), str(episode_path), *( ["--scene", args.scene] if args.scene else [] ), "--out", args.audio_dir])
    print("[4/7] Dialogue audio generated")

    conversation_manifest = ROOT / args.audio_dir / "conversation_manifest.json"
    run([sys.executable, str(ROOT / "scripts" / "build_conversation_manifest.py"), str(episode_path), "--scene", args.scene or scenes[0]["id"], "--audio-dir", args.audio_dir, "--out", str(conversation_manifest)])
    print(f"[5/7] Real-audio timing: {conversation_manifest}")

    if args.skip_video_provider:
        print("VIDEO PROVIDER SKIPPED: manifests are ready.")
        return

    provider = os.getenv("VIDEO_GENERATOR_CMD", "").strip()
    if provider:
        run(shlex.split(provider) + [str(shot_manifest), str(ROOT / args.video_dir)])
    else:
        run([
            sys.executable, str(ROOT / "scripts" / "generate_veo_videos.py"),
            str(shot_manifest), str(ROOT / args.video_dir),
            "--reaction-dir", str(ROOT / args.reaction_dir),
            "--references", str(ROOT / "outputs" / "references"),
            "--scene", args.scene or scenes[0]["id"],
        ])
    print("[6/7] Veo video shots generated")

    run([
        sys.executable,
        str(ROOT / "scripts" / "render_two_character_conversation.py"),
        str(conversation_manifest), "--video-dir", args.video_dir,
        "--reaction-dir", args.reaction_dir,
        "--wav2lip-dir", args.wav2lip_dir,
        "--checkpoint", args.checkpoint, "--out", args.out,
    ])
    print(f"[7/7] FINAL VIDEO: {ROOT / args.out}")


if __name__ == "__main__":
    main()
