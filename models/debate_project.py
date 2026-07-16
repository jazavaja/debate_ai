from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from models.debate_config import DebateConfig
from core.debate_engine import DebateTurn
from typing import List, Optional, Dict, Any
from models.debate_config import DebateConfig
from core.debate_engine import DebateTurn


@dataclass
class DebateProject:
    config: DebateConfig
    turns: List[DebateTurn] = field(default_factory=list)
    conclusion: str = ""
    exported_output_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'config': {
                'topic': self.config.topic,
                'max_turns': self.config.max_turns,
                'temperature': self.config.temperature,
                'debater1': self.config.debater1.to_dict(),
                'debater2': self.config.debater2.to_dict(),
                'moderator': self.config.moderator.to_dict(),
            },
            'turns': [
                {'speaker': t.speaker, 'content': t.content, 'turn_number': t.turn_number}
                for t in self.turns
            ],
            'conclusion': self.conclusion,
            'exported_output_path': self.exported_output_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DebateProject':
        cfg = data.get('config', {})
        from models.debater import Debater
        deb1 = Debater.from_dict(cfg.get('debater1', {}))
        deb2 = Debater.from_dict(cfg.get('debater2', {}))
        mod = Debater.from_dict(cfg.get('moderator', {}))

        debate_config = DebateConfig(
            topic=cfg.get('topic', ''),
            debater1=deb1,
            debater2=deb2,
            moderator=mod,
            max_turns=cfg.get('max_turns', 50),
            temperature=cfg.get('temperature', 0.8)
        )

        turns_data = data.get('turns', [])
        turns: List[DebateTurn] = []
        for td in turns_data:
            turns.append(DebateTurn(
                speaker=td.get('speaker', ''),
                content=td.get('content', ''),
                turn_number=td.get('turn_number', 0)
            ))

        return cls(
            config=debate_config,
            turns=turns,
            conclusion=data.get('conclusion', ''),
            exported_output_path=data.get('exported_output_path')
        )