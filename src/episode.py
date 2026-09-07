from pathlib import Path
import json
import yaml

from .validator import validate_episode
from .prompt_builder import build_image_prompt, build_video_prompt, build_voice_prompt


def load_episode(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_episode(path: str, output_root: str = "output") -> Path:
    data = load_episode(path)
    errors = validate_episode(data)
    if errors:
        raise ValueError("Invalid episode:\n- " + "\n- ".join(errors))

    out = Path(output_root) / data["id"]
    scenes_out = out / "scenes"
    scenes_out.mkdir(parents=True, exist_ok=True)

    (out / "story.md").write_text(
        f"# {data['title']}\n\n**Logline:** {data['logline']}\n\n"
        f"**Genre:** {data.get('genre', 'dark fantasy')}\n",
        encoding="utf-8",
    )

    for scene in data["scenes"]:
        image = build_image_prompt(data, scene)
        video = build_video_prompt(data, scene)
        voice = build_voice_prompt(data, scene)
        sid = scene["id"]
        (scenes_out / f"{sid}-image.md").write_text(f"# {sid} Image Prompt\n\n{image}\n", encoding="utf-8")
        (scenes_out / f"{sid}-video.md").write_text(f"# {sid} Video Prompt\n\n{video}\n", encoding="utf-8")
        (scenes_out / f"{sid}-voice.md").write_text(f"# {sid} Voice Prompt\n\n{voice}\n", encoding="utf-8")

    manifest = {
        "episode_id": data["id"],
        "title": data["title"],
        "scene_count": len(data["scenes"]),
        "status": "prompt-pack-generated",
    }
    (out / "production.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
