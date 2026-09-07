from dataclasses import dataclass, field
from typing import List

@dataclass
class Character:
    id: str
    name: str
    role: str
    appearance: str
    personality: str = ""
    continuity_notes: str = ""

@dataclass
class Scene:
    id: str
    title: str
    location: str
    time: str
    action: str
    image_prompt: str = ""
    video_prompt: str = ""
    narration: str = ""
    duration_seconds: int = 8
    status: str = "draft"

@dataclass
class Episode:
    id: str
    title: str
    logline: str
    genre: str = "dark fantasy"
    language: str = "th"
    characters: List[Character] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
