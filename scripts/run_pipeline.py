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
                "scene_id": scene["id"],
                "shot": shot,
                "location": scene.get("location", ""),
                "time": scene.get("time", ""),
                "visual_anchor": scene.get("visual_anchor", ""),
                "environment_lock": scene.get("environment_lock", ""),
                "characters": episode.get("characters", []),
                "image_prompt": pack["image"],
                "video_prompt": pack["video"],
                "dialogue": pack.get("dialogue", ""),
                "audio_direction": pack.get("audio_direction", ""),
            })
    payload = {
        "version": "2.0",
        "automation": "one-command",
        "environment_policy": "same physical environment unless the script explicitly changes location",
        "speaker_policy": "only active speaker moves mouth; listener stays silent",
        "shots": shots,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="One-command AI Drama Pipeline")
    parser.add_argument("episode")
    parser.add_argument("--scene", default=None)
    parser.add_argument("--audio-dir", default="outputs/two_character_audio")
    parser.add_argument("--video-dir", default="inputs/two_character_shots")
    parser.add_argument("--reaction-dir", default="inputs/two_character_reactions")
    parser.add_argument("--wav2lip-dir", default=os.getenv("WAV2LIP_DIR", "/content/Wav2Lip"))
    parser.add_argument("--checkpoint", default=os.getenv("WAV2LIP_CHECKPOINT", "/content/Wav2Lip/checkpoints/wav2lip_gan.pth"))
    parser.add_argument("--out", default="outputs/final/two_character_conversation.mp4")
    parser.add_argument("--skip-video-provider", action="store_true", help="Only prepare prompts/audio/timing; do not call a video provider")
    args = parser.parse_args()

    episode_path = ROOT / args.episode
    episode = yaml.safe_load(episode_path.read_text(encoding="utf-8"))
    scenes = episode.get("scenes", [])
    if args.scene:
        scenes = [s for s in scenes if s["id"] == args.scene]
        if not scenes:
            raise ValueError(f"Scene not found: {args.scene}")
        episode = {**episode, "scenes": scenes}

    automation_dir = ROOT / "outputs" / "automation"
    shot_manifest = generate_shot_manifest(episode, automation_dir / "shot_manifest.json")
    print(f"[1/4] Shot manifest: {shot_manifest}")

    run([sys.executable, str(ROOT / "scripts" / "generate_two_character_audio.py"), str(episode_path), *( ["--scene", args.scene] if args.scene else [] ), "--out", args.audio_dir])
    print("[2/4] Dialogue audio generated")

    conversation_manifest = ROOT / args.audio_dir / "conversation_manifest.json"
    run([sys.executable, str(ROOT / "scripts" / "build_conversation_manifest.py"), str(episode_path), "--scene", args.scene or scenes[0]["id"], "--audio-dir", args.audio_dir, "--out", str(conversation_manifest)])
    print(f"[3/4] Real-audio timing: {conversation_manifest}")

    if args.skip_video_provider:
        print("VIDEO PROVIDER SKIPPED: shot_manifest.json is ready for the configured video generator.")
        return

    provider = os.getenv("VIDEO_GENERATOR_CMD", "").strip()
    if provider:
        # Provider command receives the manifest path and is responsible for creating
        # speaker-specific clips named turn{N}_{SPEAKER}.mp4 in --video-dir.
        command = shlex.split(provider) + [str(shot_manifest), str(ROOT / args.video_dir)]
        run(command)
    else:
        print("VIDEO_GENERATOR_CMD is not configured. The pipeline will not fake video generation.")
        print("Configure one video-generation adapter once; then this same command will continue automatically.")
        print(f"Shot manifest ready: {shot_manifest}")
        return

    run([
        sys.executable,
        str(ROOT / "scripts" / "render_two_character_conversation.py"),
        str(conversation_manifest),
        "--video-dir", args.video_dir,
        "--reaction-dir", args.reaction_dir,
        "--wav2lip-dir", args.wav2lip_dir,
        "--checkpoint", args.checkpoint,
        "--out", args.out,
    ])
    print(f"[4/4] FINAL VIDEO: {ROOT / args.out}")


if __name__ == "__main__":
    main()
