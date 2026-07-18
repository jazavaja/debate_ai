# core/debate_engine.py
from typing import Callable, List, Optional

from PyQt5.QtCore import QThread, pyqtSignal

from core.llm_client import LLMClient
from core.moderator_agent import ModeratorAction, ModeratorAgent
from models.debate_config import DebateConfig
from models.debate_status import DebateStatus, GenerationError, TurnType
from models.debate_turn import DebateTurn
from models.debater import Debater

# Re-export for backward compatibility
__all__ = ["DebateTurn", "DebateEngineThread", "DebateEngine"]


class DebateEngineThread(QThread):
    """موتور اصلی مناظره در ترد جداگانه — با intro، مداخله، خطا و resume."""

    turn_generated = pyqtSignal(DebateTurn)
    turn_chunk = pyqtSignal(int, str)
    turn_stream_start = pyqtSignal(int, str, str)  # turn_number, speaker, turn_type
    debate_finished = pyqtSignal(str)
    debate_conclusion_chunk = pyqtSignal(str)
    error_occurred = pyqtSignal(object)  # GenerationError
    status_changed = pyqtSignal(str)
    progress_updated = pyqtSignal(int, int)

    def __init__(
        self,
        llm_client: LLMClient,
        config: DebateConfig,
        existing_turns: Optional[List[DebateTurn]] = None,
        existing_conclusion: str = "",
        resume: bool = False,
    ):
        super().__init__()
        self.llm_client = llm_client
        self.config = config
        self.existing_turns = list(existing_turns or [])
        self.existing_conclusion = existing_conclusion
        self.resume = resume
        self._is_running = True
        self._current_step = ""
        self._next_turn_number = self._calc_next_turn_number()
        self._moderator = ModeratorAgent(llm_client)

    def run(self):
        history: List[DebateTurn] = list(self.existing_turns)
        total_debater_turns = self.config.max_turns * 2

        try:
            self._emit_status(DebateStatus.RUNNING)

            # --- Step 1: Moderator Introduction ---
            if not self._has_intro(history) and not self._is_legacy_project(history):
                intro = self._generate_intro()
                history.append(intro)
                self.turn_generated.emit(intro)

            if not self._is_running:
                self._emit_status(DebateStatus.STOPPED)
                return

            # --- Step 2: Debater turns with optional moderator intervention ---
            completed = self._count_debater_turns(history)

            for turn_idx in range(completed, total_debater_turns):
                if not self._is_running:
                    self._emit_status(DebateStatus.STOPPED)
                    return

                is_debater1 = turn_idx % 2 == 0
                next_debater = self.config.debater1 if is_debater1 else self.config.debater2

                # Moderator decision (skip for very first debater turn right after intro)
                if turn_idx > 0:
                    decision = self._moderator_decide(history, next_debater.name)
                    if decision.action != ModeratorAction.CONTINUE:
                        intervention = self._generate_intervention(history, decision)
                        history.append(intervention)
                        self.turn_generated.emit(intervention)

                    if not self._is_running:
                        self._emit_status(DebateStatus.STOPPED)
                        return

                debater_turn = self._generate_debater_turn(history, turn_idx, next_debater)
                history.append(debater_turn)
                self.turn_generated.emit(debater_turn)
                self.progress_updated.emit(turn_idx + 1, total_debater_turns)

            if not self._is_running:
                self._emit_status(DebateStatus.STOPPED)
                return

            # --- Step 3: Moderator Conclusion ---
            if not self.existing_conclusion:
                conclusion = self._generate_conclusion(history)
                self.debate_finished.emit(conclusion)
            else:
                self.debate_finished.emit(self.existing_conclusion)

            self._emit_status(DebateStatus.COMPLETED)

        except Exception as e:
            error = GenerationError.now(str(e), self._current_step)
            self._emit_status(DebateStatus.FAILED)
            self.error_occurred.emit(error)

    # ------------------------------------------------------------------ #
    # Generation steps
    # ------------------------------------------------------------------ #

    def _generate_intro(self) -> DebateTurn:
        self._current_step = "moderator_intro"
        system, user = self._moderator.build_intro_prompts(self.config)
        content = self._stream_llm(
            system, user,
            turn_number=self._alloc_turn_number(),
            speaker=self.config.moderator.name,
            turn_type=TurnType.MODERATOR_INTRO,
            temperature=0.5,
        )
        self._validate_response(content, "moderator_intro")
        return DebateTurn(
            speaker=self.config.moderator.name,
            content=content,
            turn_number=self._next_turn_number - 1,
            turn_type=TurnType.MODERATOR_INTRO,
        )

    def _moderator_decide(self, history: List[DebateTurn], next_speaker: str):
        self._current_step = "moderator_decision"
        return self._moderator.decide(self.config, history, next_speaker)

    def _generate_intervention(self, history: List[DebateTurn], decision) -> DebateTurn:
        self._current_step = f"moderator_intervention_{decision.action.value}"
        system, user = self._moderator.build_intervention_prompts(
            self.config, history, decision
        )
        turn_num = self._alloc_turn_number()
        content = self._stream_llm(
            system, user,
            turn_number=turn_num,
            speaker=self.config.moderator.name,
            turn_type=TurnType.MODERATOR_INTERVENTION,
            temperature=0.5,
        )
        self._validate_response(content, self._current_step)
        return DebateTurn(
            speaker=self.config.moderator.name,
            content=content,
            turn_number=turn_num,
            turn_type=TurnType.MODERATOR_INTERVENTION,
        )

    def _generate_debater_turn(
        self,
        history: List[DebateTurn],
        turn_idx: int,
        debater: Debater,
    ) -> DebateTurn:
        self._current_step = f"debater_turn_{turn_idx + 1}"
        base_system = f"""شما در یک مناظره هوش مصنوعی شرکت دارید.
موضوع مناظره: {self.config.topic}

قوانین:
- فقط متن صحبت خودتان را بنویسید
- از توضیحات اضافی، پیش‌درآمد یا پس‌درآمد خودداری کنید
- پاسخ باید طبیعی، استدلالی و متقاعدکننده باشد
- به طرف مقابل اشاره مستقیم نکنید، صحبت خودتان را بکنید
- پاسخ حداکثر ۳-۴ پاراگراف باشد"""

        system_prompt = f"""{base_system}

شخصیت شما: {debater.name}
{debater.prompt}"""

        user_prompt = self._build_debater_prompt(debater, history)
        turn_num = self._alloc_turn_number()
        content = self._stream_llm(
            system_prompt, user_prompt,
            turn_number=turn_num,
            speaker=debater.name,
            turn_type=TurnType.DEBATER,
            temperature=self.config.temperature,
        )
        self._validate_response(content, self._current_step)
        return DebateTurn(
            speaker=debater.name,
            content=content,
            turn_number=turn_num,
            turn_type=TurnType.DEBATER,
        )

    def _generate_conclusion(self, history: List[DebateTurn]) -> str:
        self._current_step = "moderator_conclusion"
        system, user = self._moderator.build_conclusion_prompts(self.config, history)
        conclusion_text = ""

        def _on_chunk(chunk: str):
            nonlocal conclusion_text
            conclusion_text += chunk
            self.debate_conclusion_chunk.emit(chunk)

        self.llm_client.chat_stream(
            system, user, _on_chunk, temperature=0.5, raise_on_error=True
        )
        self._validate_response(conclusion_text, "moderator_conclusion")
        return conclusion_text

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _stream_llm(
        self,
        system: str,
        user: str,
        turn_number: int,
        speaker: str,
        turn_type: TurnType,
        temperature: float,
    ) -> str:
        self.turn_stream_start.emit(turn_number, speaker, turn_type.value)
        response_text = ""

        def _on_chunk(chunk: str):
            nonlocal response_text
            response_text += chunk
            self.turn_chunk.emit(turn_number, chunk)

        self.llm_client.chat_stream(
            system, user, _on_chunk, temperature, raise_on_error=True
        )
        return response_text

    def _validate_response(self, content: str, step: str):
        if not content or not content.strip():
            raise ValueError(f"Invalid empty response at step: {step}")
        if content.strip().startswith("[خطا"):
            raise RuntimeError(f"LLM error at step {step}: {content.strip()}")

    def _build_debater_prompt(self, debater: Debater, history: List[DebateTurn]) -> str:
        parts = [f"موضوع: {self.config.topic}\n", f"شما {debater.name} هستید.\n"]
        if history:
            parts.append("مکالمات قبلی:\n")
            for turn in history[-5:]:
                parts.append(f"{turn.speaker}: {turn.content}\n")
        parts.append("\nحالا نوبت شماست. لطفاً صحبت خودتان را انجام دهید:")
        return "\n".join(parts)

    def _has_intro(self, history: List[DebateTurn]) -> bool:
        return any(t.turn_type == TurnType.MODERATOR_INTRO for t in history)

    def _is_legacy_project(self, history: List[DebateTurn]) -> bool:
        """Projects saved before moderator intro have debater turns but no intro."""
        return self.resume and self._count_debater_turns(history) > 0 and not self._has_intro(history)

    def _count_debater_turns(self, history: List[DebateTurn]) -> int:
        return sum(1 for t in history if t.turn_type == TurnType.DEBATER)

    def _calc_next_turn_number(self) -> int:
        if not self.existing_turns:
            return 1
        return max(t.turn_number for t in self.existing_turns) + 1

    def _alloc_turn_number(self) -> int:
        num = self._next_turn_number
        self._next_turn_number += 1
        return num

    def _emit_status(self, status: DebateStatus):
        self.status_changed.emit(status.value)

    def stop(self):
        self._is_running = False
        self.wait(1000)


class DebateEngine:
    """فکتوری و کنترلر موتور مناظره."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self._current_thread: Optional[DebateEngineThread] = None

    def start_debate(
        self,
        config: DebateConfig,
        on_turn: Callable,
        on_finish: Callable,
        on_error: Callable,
        on_progress: Callable,
        on_chunk: Callable = None,
        on_conclusion_chunk: Callable = None,
        on_stream_start: Callable = None,
        on_status_changed: Callable = None,
        existing_turns: Optional[List[DebateTurn]] = None,
        existing_conclusion: str = "",
        resume: bool = False,
    ) -> DebateEngineThread:
        self.stop_debate()

        thread = DebateEngineThread(
            self.llm_client,
            config,
            existing_turns=existing_turns,
            existing_conclusion=existing_conclusion,
            resume=resume,
        )
        thread.turn_generated.connect(on_turn)
        if on_chunk:
            thread.turn_chunk.connect(on_chunk)
        if on_stream_start:
            thread.turn_stream_start.connect(on_stream_start)
        thread.debate_finished.connect(on_finish)
        if on_conclusion_chunk:
            thread.debate_conclusion_chunk.connect(on_conclusion_chunk)
        thread.error_occurred.connect(on_error)
        thread.progress_updated.connect(on_progress)
        if on_status_changed:
            thread.status_changed.connect(on_status_changed)

        self._current_thread = thread
        thread.start()
        return thread

    def stop_debate(self):
        if self._current_thread and self._current_thread.isRunning():
            self._current_thread.stop()
            self._current_thread = None
