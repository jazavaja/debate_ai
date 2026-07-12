# models/debater.py
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Debater:
    """مدل داده‌ای مذاکره‌کننده"""
    name: str = ""
    prompt: str = ""
    role: str = "debater"  # 'debater' یا 'moderator'

    def __post_init__(self):
        if not self.name:
            self.name = "ناشناس"

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'prompt': self.prompt,
            'role': self.role
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Debater':
        return cls(**data)