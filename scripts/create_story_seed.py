import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.story_engine import generate_story_seed


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a deterministic AI Drama story seed")
    parser.add_argument("premise", help="Story premise")
    parser.add_argument("--title", default="Untitled Episode")
    parser.add_argument("--output", default="output/story_seed.json")
    args = parser.parse_args()

    story = generate_story_seed(args.premise, title=args.title)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Story seed written to {output}")


if __name__ == "__main__":
    main()
