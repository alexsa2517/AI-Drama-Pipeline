from __future__ import annotations

from typing import Any

SOUND_DIRECTOR_MASTER = """AI SOUND DIRECTOR
Choose music, ambience, Foley, SFX and silence from story, emotion, action, location, time, pacing and dramatic purpose.
Music is optional. Silence is deliberate. Every cue needs reason, timing, intensity and exit.
Ambience must belong to the physical world. Foley follows visible action and material/weight/distance.
SFX is story-motivated and perspective-correct. Dialogue remains intelligible.
Preserve sound continuity across cuts.
"""


def _text(scene: dict[str, Any], *keys: str) -> str:
    return " ".join(str(scene.get(k, "")) for k in keys if scene.get(k))


def _emotion(scene: dict[str, Any]) -> str:
    return str(scene.get("emotion") or scene.get("emotional_beat") or "natural").strip().lower()


def _tension(scene: dict[str, Any]) -> float:
    raw = scene.get("tension", scene.get("tension_level"))
    try:
        value = float(raw)
        return max(0.0, min(1.0, value / 100 if value > 1 else value))
    except (TypeError, ValueError):
        e = _emotion(scene)
        if any(x in e for x in ("fear", "terror", "danger", "angry", "panic", "threat", "กลัว", "อันตราย", "โกรธ")):
            return .75
        if any(x in e for x in ("sad", "grief", "loss", "เศร้า", "สูญเสีย")):
            return .55
        if any(x in e for x in ("wonder", "calm", "สงบ", "sacred", "ศักดิ์สิทธิ์")):
            return .25
        return .4


def _function(scene: dict[str, Any]) -> str:
    text = _text(scene, "story_purpose", "reveal", "story_question", "action", "conflict", "payoff").lower()
    if any(x in text for x in ("climax", "final", "payoff", "จุดไคลแมกซ์", "บทสรุป", "เฉลย")):
        return "climax/payoff"
    if any(x in text for x in ("reveal", "discovery", "mystery", "เปิดเผย", "ค้นพบ", "ความลับ")):
        return "reveal/discovery"
    if any(x in text for x in ("danger", "threat", "conflict", "pursuit", "อันตราย", "ภัย", "ความขัดแย้ง")):
        return "tension/threat"
    return "setup/character beat"


def _music(scene: dict[str, Any]) -> dict[str, Any]:
    emotion, function, tension = _emotion(scene), _function(scene), _tension(scene)
    if function == "reveal/discovery": style = "minimal mysterious atmospheric score"
    elif function == "climax/payoff": style = "cinematic emotional score with controlled build and release"
    elif function == "tension/threat": style = "restrained low-frequency tension score with sparse pulses"
    elif any(x in emotion for x in ("sacred", "wonder", "calm", "สงบ", "ศักดิ์สิทธิ์")): style = "sparse atmospheric score with organic acoustic texture"
    else: style = "subtle scene-supporting underscore"
    return {"use": tension >= .3 or function != "setup/character beat", "style": style, "intensity": round(min(.72, max(.12, tension * .75)), 2)}


def _ambience(scene: dict[str, Any]) -> list[str]:
    location = str(scene.get("location", "")).lower()
    time = str(scene.get("time", scene.get("time_of_day", ""))).lower()
    weather = str(scene.get("weather", "")).lower()
    if any(x in location for x in ("temple", "วัด", "ศาล", "monastery", "pagoda")):
        result = ["distant temple ambience", "soft wind through architecture", "subtle birds/insects when plausible"]
    elif any(x in location for x in ("forest", "ป่า", "jungle")):
        result = ["layered forest air", "distant insects", "occasional birds", "soft leaves/wind"]
    elif any(x in location for x in ("market", "ตลาด", "street", "ถนน", "เมือง", "city")):
        result = ["distant human activity", "occasional footsteps", "plausible traffic/carts"]
    elif any(x in location for x in ("room", "house", "hut", "ห้อง", "บ้าน")):
        result = ["quiet interior room tone", "subtle structure/cloth sounds", "appropriate air movement"]
    else:
        result = ["location-appropriate environmental bed inferred from the scene"]
    if any(x in weather for x in ("rain", "ฝน")): result.append("rain matched to intensity and distance")
    if any(x in weather for x in ("wind", "ลม")): result.append("wind matched to visible environmental movement")
    if any(x in time for x in ("night", "กลางคืน")): result.append("night ambience with reduced daytime activity")
    return result


def _sfx(scene: dict[str, Any]) -> list[str]:
    action = _text(scene, "action", "movement", "objects", "reveal").lower()
    rules = [
        (("walk", "เดิน", "step", "foot"), "footsteps matched to surface, speed and character weight"),
        (("door", "ประตู", "open", "ปิด"), "door/contact Foley matched to material and force"),
        (("weapon", "ดาบ", "sword", "impact", "ชน", "กระแทก"), "precise story-critical impact/contact SFX"),
        (("water", "น้ำ", "river", "แม่น้ำ"), "water contact/movement only when visible or justified"),
        (("fire", "ไฟ", "flame"), "subtle fire crackle when visible"),
    ]
    found = [cue for tokens, cue in rules if any(t in action for t in tokens)]
    return found or ["No generic SFX; add only sounds motivated by visible action or story events"]


def build_ai_sound_director(episode: dict, scene: dict, scene_index: int = 0) -> str:
    music, ambience, sfx = _music(scene), _ambience(scene), _sfx(scene)
    duration = scene.get("duration") or scene.get("duration_seconds") or "auto"
    lines = [SOUND_DIRECTOR_MASTER, "SCENE SOUND DIRECTOR PLAN", f"Scene: {scene.get('id', scene_index + 1)}", f"Function: {_function(scene)}", f"Emotion: {_emotion(scene)}", f"Tension: {_tension(scene):.2f}", f"Duration: {duration}", f"Location: {scene.get('location', 'unspecified')}", "", "MUSIC DECISION", f"Use music: {'YES' if music['use'] else 'NO / SILENCE-FIRST'}", f"Style: {music['style']}", f"Intensity: {music['intensity']:.2f}", "Entry/exit must follow dramatic beats; never use wall-to-wall filler.", "", "NATURAL / AMBIENT SOUND"]
    lines.extend(f"- {x}" for x in ambience)
    lines += ["", "FOLEY / SFX"]
    lines.extend(f"- {x}" for x in sfx)
    lines += ["", "DRAMATIC TIMING", "- Establish the acoustic world at the opening.", "- Before important dialogue/reveal: reduce competing sound or use controlled silence.", "- During action: sync foreground Foley/SFX to visible movement.", "- After reveal/important line: allow a reaction tail.", "- Scene exit: carry or intentionally transform sound into the next scene.", "", "MIX", "Dialogue remains intelligible. Duck music/ambience around critical words while preserving depth.", "", "OUTPUT", "Return cue timeline with start/end or relative beat, type, purpose, intensity, fade and transition. Use short cues for impacts, medium cues for phrases, and long beds only when sustained atmosphere is justified."]
    return "\n".join(lines)


def build_sound_cue_timeline(episode: dict, scene: dict, scene_index: int = 0) -> list[dict[str, Any]]:
    music = _music(scene)
    cues: list[dict[str, Any]] = []
    if music["use"]:
        cues.append({"type": "music", "cue": music["style"], "start": "dramatic_entry", "end": "dramatic_exit", "intensity": music["intensity"], "fade_in": "1-2s", "fade_out": "1-3s"})
    for item in _ambience(scene):
        cues.append({"type": "ambience", "cue": item, "start": 0, "end": "scene_end", "intensity": .2, "duration": "long_bed"})
    for item in _sfx(scene):
        if not item.startswith("No generic"):
            cues.append({"type": "sfx", "cue": item, "start": "action_sync", "end": "action_sync+tail", "intensity": .45, "duration": "short"})
    return cues
