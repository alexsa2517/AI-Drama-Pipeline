from pathlib import Path
import json
import yaml

from .validator import validate_episode
from .prompt_pack import build_scene_pack
from .feature_film_story import build_legend_story_prompt
from .quality import quality_report
from .director_loop import start_director_loop


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

    if str(data.get("content_type", "")).lower() == "legend" or str(data.get("genre", "")).lower() in {"legend", "folklore", "myth", "mythology", "dark folklore thriller"}:
        (out / "story_blueprint.md").write_text(build_legend_story_prompt(data) + "\n", encoding="utf-8")

    scene_packs = build_scene_pack(data)
    loop_manifest = {"episode_id": data["id"], "workflow": "DIRECT → RENDER → EVALUATE → DECIDE → REVISE → RENDER AGAIN", "max_iterations": 3, "scenes": []}
    for index, pack in enumerate(scene_packs):
        sid = pack["scene_id"]
        (scenes_out / f"{sid}-image.md").write_text(
            f"# {sid} Image Prompt\n\n{pack['image']}\n", encoding="utf-8"
        )
        (scenes_out / f"{sid}-video.md").write_text(
            f"# {sid} Video Prompt\n\n{pack['video']}\n", encoding="utf-8"
        )
        (scenes_out / f"{sid}-voice.md").write_text(
            f"# {sid} Voice Prompt\n\n{pack['voice']}\n", encoding="utf-8"
        )
        state = start_director_loop(data, data["scenes"][index], max_iterations=3)
        loop_manifest["scenes"].append({
            "scene_id": sid,
            "initial_state": state.status,
            "max_iterations": state.max_iterations,
            "rule": "revise only the smallest failing shot/layer and preserve all passing locked elements",
        })

    report = quality_report(data)
    (out / "quality.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "director_loop.json").write_text(
        json.dumps(loop_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    manifest = {
        "episode_id": data["id"],
        "title": data["title"],
        "scene_count": len(data["scenes"]),
        "quality": report,
        "director_loop": "DIRECT → RENDER → EVALUATE → DECIDE → REVISE → RENDER AGAIN",
        "status": "ready-for-human-review" if report["ready"] else "quality-gate-failed",
    }
    (out / "production.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out
