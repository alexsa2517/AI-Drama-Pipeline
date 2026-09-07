from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow direct execution from the repository root or from any working directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml
from gtts import gTTS

from src.dialogue_scene import normalize_dialogue


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate one Thai audio file per dialogue turn.')
    parser.add_argument('episode')
    parser.add_argument('--scene', default=None)
    parser.add_argument('--out', default='outputs/two_character_audio')
    args = parser.parse_args()

    episode = yaml.safe_load(Path(args.episode).read_text(encoding='utf-8'))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []

    for scene in episode.get('scenes', []):
        if args.scene and scene['id'] != args.scene:
            continue
        for turn in normalize_dialogue(scene):
            speaker = turn['speaker']
            text = turn['dialogue']
            path = out / f"{scene['id']}_turn{turn['turn']}_{speaker}.mp3"
            voice = next((c.get('voice', {}) for c in episode.get('characters', []) if c.get('id') == speaker), {})
            lang = voice.get('language', episode.get('language', 'th'))
            gTTS(text=text, lang=lang, slow=bool(voice.get('slow', False))).save(str(path))
            results.append({
                'scene_id': scene['id'],
                'turn': turn['turn'],
                'speaker': speaker,
                'dialogue': text,
                'audio': str(path),
                'language': lang,
                'pause_after': float(turn.get('pause_after', 0.25)),
                'emotion': turn.get('emotion', 'natural'),
                'delivery': turn.get('delivery', 'natural conversational delivery'),
            })

    manifest = out / 'manifest.json'
    manifest.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Generated {len(results)} dialogue tracks: {manifest}')


if __name__ == '__main__':
    main()
