from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lip-sync each active-speaker shot with Wav2Lip, preserve silent listener reactions, add exact pauses, and concatenate the conversation."
    )
    parser.add_argument("manifest", help="conversation_manifest.json")
    parser.add_argument("--video-dir", default="inputs/two_character_shots")
    parser.add_argument("--reaction-dir", default="inputs/two_character_reactions")
    parser.add_argument("--wav2lip-dir", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--out", default="outputs/final/two_character_conversation.mp4")
    parser.add_argument("--keep-intermediate", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    video_dir = Path(args.video_dir)
    reaction_dir = Path(args.reaction_dir)
    work = Path("outputs/two_character_render")
    work.mkdir(parents=True, exist_ok=True)
    final_out = Path(args.out)
    final_out.parent.mkdir(parents=True, exist_ok=True)

    concat_entries: list[Path] = []

    for item in manifest["turns"]:
        turn = item["turn"]
        speaker = item["speaker"]
        audio = Path(item["audio"])
        source = video_dir / f"turn{turn}_{speaker}.mp4"
        if not source.exists():
            raise FileNotFoundError(
                f"Missing active-speaker shot: {source}. "
                "Create/upload one shot per dialogue turn with the active speaker clearly framed."
            )

        synced = work / f"turn{turn}_{speaker}_lipsync.mp4"
        run([
            sys.executable,
            str(Path(args.wav2lip_dir) / "inference.py"),
            "--checkpoint_path", str(Path(args.checkpoint).resolve()),
            "--face", str(source.resolve()),
            "--audio", str(audio.resolve()),
            "--outfile", str(synced.resolve()),
        ])

        # Make the pause after this turn part of the same A/V segment.
        # The dialogue audio is preserved; the appended interval is true silence.
        pause = max(0.0, float(item.get("pause_after", 0.25)))
        if pause > 0:
            paused = work / f"turn{turn}_{speaker}_with_pause.mp4"
            duration = float(item["audio_duration"]) + pause
            run([
                "ffmpeg", "-y", "-i", str(synced.resolve()),
                "-vf", f"tpad=stop_mode=clone:stop_duration={pause}",
                "-af", f"apad=pad_dur={pause}",
                "-t", f"{duration:.3f}",
                "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p", str(paused.resolve()),
            ])
            concat_entries.append(paused)
        else:
            concat_entries.append(synced)

        # Optional silent listener reaction. This clip is never sent through Wav2Lip,
        # so the listener's mouth remains silent while blinking/gazing/reacting naturally.
        reaction = reaction_dir / f"turn{turn}_{item['listener']}.mp4"
        if reaction.exists():
            reaction_out = work / f"turn{turn}_reaction.mp4"
            run([
                "ffmpeg", "-y", "-i", str(reaction.resolve()),
                "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                str(reaction_out.resolve()),
            ])
            concat_entries.append(reaction_out)

    concat_file = work / "concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in concat_entries) + "\n",
        encoding="utf-8",
    )

    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file.resolve()),
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(final_out.resolve()),
    ])

    print(f"FINAL VIDEO: {final_out.resolve()}")
    print(f"Segments: {len(concat_entries)}")
    print("Speaker/listener contract: active speaker lip-sync only; listener silent.")
    print("Environment contract: all source shots must depict the same physical location.")
    if args.keep_intermediate:
        print("Intermediate files kept in outputs/two_character_render.")


if __name__ == "__main__":
    main()
