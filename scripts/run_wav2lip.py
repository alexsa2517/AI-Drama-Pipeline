from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Wav2Lip on a generated scene video and character dialogue audio.")
    parser.add_argument("--video", required=True, help="Input scene video")
    parser.add_argument("--audio", required=True, help="Character dialogue WAV/MP3")
    parser.add_argument("--checkpoint", required=True, help="Wav2Lip checkpoint path")
    parser.add_argument("--wav2lip-dir", required=True, help="Local Wav2Lip repository directory")
    parser.add_argument("--out", required=True, help="Output lip-synced video")
    args = parser.parse_args()

    video = Path(args.video).resolve()
    audio = Path(args.audio).resolve()
    checkpoint = Path(args.checkpoint).resolve()
    wav2lip_dir = Path(args.wav2lip_dir).resolve()
    output = Path(args.out).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "python",
        str(wav2lip_dir / "inference.py"),
        "--checkpoint_path", str(checkpoint),
        "--face", str(video),
        "--audio", str(audio),
        "--outfile", str(output),
    ]
    print("Running lip-sync:")
    print(" ".join(command))
    subprocess.run(command, cwd=str(wav2lip_dir), check=True)
    print(f"Lip-synced video: {output}")


if __name__ == "__main__":
    main()
