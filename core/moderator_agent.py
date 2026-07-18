# core/moderator_agent.py
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from core.llm_client import LLMClient
from core.moderator_prompts import (
    ACTION_INSTRUCTIONS,
    ACTION_LABELS,
    CONCLUSION_SYSTEM,
    CONCLUSION_USER,
    DECISION_SYSTEM,
    DECISION_USER,
    INTRO_SYSTEM,
    INTRO_USER,
    INTERVENTION_SYSTEM,
    INTERVENTION_USER,
)
from models.debate_config import DebateConfig


class ModeratorAction(str, Enum):
    CONTINUE = "continue"
    ASK_QUESTION = "ask_question"
    SUMMARIZE = "summarize"
    CHALLENGE = "challenge_speaker"


@dataclass
class ModeratorDecision:
    action: ModeratorAction
    reason: str = ""
    target_speaker: str = ""


class ModeratorAgent:
    """Decision layer for moderator — decides when and how to intervene."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def build_intro_prompts(self, config: DebateConfig) -> Tuple[str, str]:
        system = INTRO_SYSTEM.format(moderator_prompt=config.moderator.prompt)
        user = INTRO_USER.format(
            topic=config.topic,
            debater1_name=config.debater1.name,
            debater1_prompt=config.debater1.prompt,
            debater2_name=config.debater2.name,
            debater2_prompt=config.debater2.prompt,
        )
        return system, user

    def decide(
        self,
        config: DebateConfig,
        history: list,
        next_speaker: str,
    ) -> ModeratorDecision:
        """Ask LLM whether to intervene before the next debater turn."""
        history_text = self._format_history(history, limit=8)
        system = DECISION_SYSTEM.format(moderator_prompt=config.moderator.prompt)
        user = DECISION_USER.format(
            topic=config.topic,
            next_speaker=next_speaker,
            history=history_text or "(هنوز مکالمه‌ای انجام نشده)",
        )

        raw = self.llm_client.chat(system, user, temperature=0.3)
        return self._parse_decision(raw)

    def build_intervention_prompts(
        self,
        config: DebateConfig,
        history: list,
        decision: ModeratorDecision,
    ) -> Tuple[str, str]:
        action_key = decision.action.value
        label = ACTION_LABELS.get(action_key, action_key)
        instruction = ACTION_INSTRUCTIONS.get(action_key, "").format(
            target_speaker=decision.target_speaker or "طرف مقابل"
        )

        system = INTERVENTION_SYSTEM.format(
            moderator_prompt=config.moderator.prompt,
            action_label=label,
            action_instruction=instruction,
        )
        user = INTERVENTION_USER.format(
            topic=config.topic,
            reason=decision.reason,
            recent_history=self._format_history(history, limit=5),
        )
        return system, user

    def build_conclusion_prompts(
        self,
        config: DebateConfig,
        history: list,
    ) -> Tuple[str, str]:
        system = CONCLUSION_SYSTEM.format(moderator_prompt=config.moderator.prompt)
        user = CONCLUSION_USER.format(
            topic=config.topic,
            debate_summary=self._format_history(history),
        )
        return system, user

    def _format_history(self, history: list, limit: Optional[int] = None) -> str:
        turns = history[-limit:] if limit else history
        return "\n\n".join(f"{t.speaker}:\n{t.content}" for t in turns)

    def _parse_decision(self, raw: str) -> ModeratorDecision:
        raw = raw.strip()
        if raw.startswith("[خطا"):
            raise RuntimeError(raw)

        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            return ModeratorDecision(action=ModeratorAction.CONTINUE, reason="پاسخ نامعتبر")

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parsing error in moderator decision: {e}") from e

        action_str = data.get("action", "continue")
        try:
            action = ModeratorAction(action_str)
        except ValueError:
            action = ModeratorAction.CONTINUE

        return ModeratorDecision(
            action=action,
            reason=data.get("reason", ""),
            target_speaker=data.get("target_speaker", ""),
        )
