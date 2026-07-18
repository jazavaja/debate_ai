# models/debate_turn.py
from dataclasses import dataclass

from models.debate_status import TurnType


@dataclass
class DebateTurn:
    speaker: str
    content: str
    turn_number: int
    turn_type: TurnType = TurnType.DEBATER

    def to_dict(self) -> dict:
        return {
            "speaker": self.speaker,
            "content": self.content,
            "turn_number": self.turn_number,
            "turn_type": self.turn_type.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DebateTurn":
        turn_type_str = data.get("turn_type", TurnType.DEBATER.value)
        try:
            turn_type = TurnType(turn_type_str)
        except ValueError:
            turn_type = TurnType.DEBATER
        return cls(
            speaker=data.get("speaker", ""),
            content=data.get("content", ""),
            turn_number=data.get("turn_number", 0),
            turn_type=turn_type,
        )
