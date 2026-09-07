import argparse
from .episode import generate_episode


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Drama Pipeline V1")
    parser.add_argument("episode", help="Path to episode YAML")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()
    result = generate_episode(args.episode, args.output)
    print(f"Prompt pack generated: {result}")


if __name__ == "__main__":
    main()
