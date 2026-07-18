# models/debate_status.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DebateStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class TurnType(str, Enum):
    DEBATER = "debater"
    MODERATOR_INTRO = "moderator_intro"
    MODERATOR_INTERVENTION = "moderator_intervention"


@dataclass
class GenerationError:
    message: str
    step: str
    timestamp: str

    @classmethod
    def now(cls, message: str, step: str) -> "GenerationError":
        return cls(
            message=message,
            step=step,
            timestamp=datetime.now().isoformat(timespec="seconds"),
        )

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "step": self.step,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional["GenerationError"]:
        if not data:
            return None
        return cls(
            message=data.get("message", ""),
            step=data.get("step", ""),
            timestamp=data.get("timestamp", ""),
        )
