from __future__ import annotations

import argparse
import json
from pathlib import Path

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
            })

    manifest = out / 'manifest.json'
    manifest.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Generated {len(results)} dialogue tracks: {manifest}')


if __name__ == '__main__':
    main()
