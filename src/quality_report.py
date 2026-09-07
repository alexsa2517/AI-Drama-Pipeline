from __future__ import annotations

from pathlib import Path
import json
import yaml

from .quality import quality_report


def generate_quality_report(episode_path: str, output: str | None = None) -> dict:
    with open(episode_path, "r", encoding="utf-8") as f:
        episode = yaml.safe_load(f)
    report = quality_report(episode)
    if output:
        Path(output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
