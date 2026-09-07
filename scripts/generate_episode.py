#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.episode import generate_episode


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate an AI Drama prompt pack")
    parser.add_argument("episode", help="Episode YAML file")
    parser.add_argument("--output", default="output")
    args = parser.parse_args()
    print(f"Generated: {generate_episode(args.episode, args.output)}")
