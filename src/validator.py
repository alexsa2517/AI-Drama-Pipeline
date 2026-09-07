REQUIRED_SCENE_FIELDS = ("id", "title", "location", "time", "action")


def validate_scene(scene: dict) -> list[str]:
    errors = []
    for field in REQUIRED_SCENE_FIELDS:
        if not scene.get(field):
            errors.append(f"scene missing required field: {field}")
    duration = scene.get("duration_seconds", 8)
    if not isinstance(duration, int) or duration <= 0:
        errors.append("duration_seconds must be a positive integer")
    return errors


def validate_episode(data: dict) -> list[str]:
    errors = []
    for field in ("id", "title", "logline"):
        if not data.get(field):
            errors.append(f"episode missing required field: {field}")
    scenes = data.get("scenes", [])
    if not isinstance(scenes, list) or not scenes:
        errors.append("episode must contain at least one scene")
    else:
        for index, scene in enumerate(scenes, 1):
            for error in validate_scene(scene):
                errors.append(f"scene {index}: {error}")
    return errors
