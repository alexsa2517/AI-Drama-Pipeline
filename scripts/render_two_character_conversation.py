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
        description="Lip-sync each active-speaker shot with Wav2Lip, add silent reaction clips, and concatenate the conversation."
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

        # Each source shot must frame the active speaker clearly. This prevents Wav2Lip
        # from accidentally animating the listener in a wide two-face shot.
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
        concat_entries.append(synced)

        # Optional silent listener reaction after the spoken line. If absent, the
        # lip-synced active-speaker shot is used continuously through the pause.
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
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(final_out.resolve()),
    ])

    print(f"FINAL VIDEO: {final_out.resolve()}")
    print(f"Segments: {len(concat_entries)}")
    if not args.keep_intermediate:
        print("Intermediate render files kept in outputs/two_character_render for debugging.")


if __name__ == "__main__":
    main()
