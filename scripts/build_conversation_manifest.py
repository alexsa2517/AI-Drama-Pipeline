from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml

from src.dialogue_scene import normalize_dialogue


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path)
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a two-character conversation manifest using real audio durations.")
    parser.add_argument("episode")
    parser.add_argument("--scene", required=True)
    parser.add_argument("--audio-dir", default="outputs/two_character_audio")
    parser.add_argument("--out", default="outputs/two_character_audio/conversation_manifest.json")
    args = parser.parse_args()

    episode_path = Path(args.episode)
    episode = yaml.safe_load(episode_path.read_text(encoding="utf-8"))
    scene = next(s for s in episode.get("scenes", []) if s["id"] == args.scene)
    turns = normalize_dialogue(scene)
    audio_dir = Path(args.audio_dir)

    speakers = []
    for turn in turns:
        if turn["speaker"] not in speakers:
            speakers.append(turn["speaker"])
    if len(speakers) != 2:
        raise ValueError(f"Expected exactly 2 speakers, found {len(speakers)}: {speakers}")

    timeline = []
    cursor = 0.0
    for turn in turns:
        audio = audio_dir / f"{scene['id']}_turn{turn['turn']}_{turn['speaker']}.mp3"
        if not audio.exists():
            raise FileNotFoundError(f"Missing audio: {audio}")
        duration = probe_duration(audio)
        listener = next(s for s in speakers if s != turn["speaker"])
        pause = float(turn.get("pause_after", 0.25))
        item = {
            "turn": turn["turn"],
            "speaker": turn["speaker"],
            "listener": listener,
            "dialogue": turn["dialogue"],
            "emotion": turn.get("emotion", "natural"),
            "delivery": turn.get("delivery", "natural conversational delivery"),
            "audio": str(audio),
            "audio_duration": round(duration, 3),
            "start": round(cursor, 3),
            "end": round(cursor + duration, 3),
            "pause_after": pause,
            "pause_start": round(cursor + duration, 3),
            "pause_end": round(cursor + duration + pause, 3),
            "active_mouth": turn["speaker"],
            "silent_listener": listener,
        }
        timeline.append(item)
        cursor += duration + pause

    manifest = {
        "scene_id": scene["id"],
        "title": scene.get("title", ""),
        "location": scene.get("location", ""),
        "environment_lock": scene.get("environment_lock", ""),
        "visual_anchor": scene.get("visual_anchor", ""),
        "characters": [c for c in episode.get("characters", []) if c.get("id") in speakers],
        "speakers": speakers,
        "timing_source": "real_audio_duration_from_ffprobe",
        "total_duration": round(cursor, 3),
        "turns": timeline,
        "render_contract": {
            "same_physical_environment": True,
            "camera_changes_allowed": True,
            "active_speaker_mouth_only": True,
            "listener_mouth_silent": True,
            "listener_natural_blink_gaze_reaction": True,
            "actual_audio_duration_is_authoritative": True,
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(out), "turns": len(timeline), "total_duration": round(cursor, 3)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
