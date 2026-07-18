from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models.debate_config import DebateConfig
from models.debate_status import DebateStatus, GenerationError, TurnType
from models.debate_turn import DebateTurn


@dataclass
class DebateProject:
    config: DebateConfig
    turns: List[DebateTurn] = field(default_factory=list)
    conclusion: str = ""
    exported_output_path: Optional[str] = None
    status: DebateStatus = DebateStatus.PENDING
    generation_error: Optional[GenerationError] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config": {
                "topic": self.config.topic,
                "max_turns": self.config.max_turns,
                "temperature": self.config.temperature,
                "debater1": self.config.debater1.to_dict(),
                "debater2": self.config.debater2.to_dict(),
                "moderator": self.config.moderator.to_dict(),
            },
            "turns": [t.to_dict() for t in self.turns],
            "conclusion": self.conclusion,
            "exported_output_path": self.exported_output_path,
            "status": self.status.value,
            "generation_error": (
                self.generation_error.to_dict() if self.generation_error else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DebateProject":
        cfg = data.get("config", {})
        from models.debater import Debater

        deb1 = Debater.from_dict(cfg.get("debater1", {}))
        deb2 = Debater.from_dict(cfg.get("debater2", {}))
        mod = Debater.from_dict(cfg.get("moderator", {}))

        debate_config = DebateConfig(
            topic=cfg.get("topic", ""),
            debater1=deb1,
            debater2=deb2,
            moderator=mod,
            max_turns=cfg.get("max_turns", 50),
            temperature=cfg.get("temperature", 0.8),
        )

        turns = [DebateTurn.from_dict(td) for td in data.get("turns", [])]

        status_str = data.get("status", DebateStatus.PENDING.value)
        try:
            status = DebateStatus(status_str)
        except ValueError:
            status = DebateStatus.PENDING

        return cls(
            config=debate_config,
            turns=turns,
            conclusion=data.get("conclusion", ""),
            exported_output_path=data.get("exported_output_path"),
            status=status,
            generation_error=GenerationError.from_dict(data.get("generation_error")),
        )

    def is_resumable(self) -> bool:
        if self.status == DebateStatus.COMPLETED:
            return False
        if self.status in (DebateStatus.FAILED, DebateStatus.STOPPED, DebateStatus.RUNNING):
            return True
        if self.status == DebateStatus.PENDING and self.turns:
            return True
        return False

    def debater_turns_completed(self) -> int:
        return sum(1 for t in self.turns if t.turn_type == TurnType.DEBATER)

    def has_intro(self) -> bool:
        return any(t.turn_type == TurnType.MODERATOR_INTRO for t in self.turns)
