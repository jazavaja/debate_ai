# core/debate_engine.py
from typing import List, Callable, Optional
from dataclasses import dataclass
from PyQt5.QtCore import QThread, pyqtSignal
from .llm_client import LLMClient
from models.debate_config import DebateConfig
from models.debater import Debater


@dataclass
class DebateTurn:
    """یک نوبت از مناظره"""
    speaker: str
    content: str
    turn_number: int


class DebateEngineThread(QThread):
    """
    موتور اصلی مناظره در ترد جداگانه
    """
    turn_generated = pyqtSignal(DebateTurn)  # هر نوبت تولید شد
    debate_finished = pyqtSignal(str)  # مناظره تموم شد
    error_occurred = pyqtSignal(str)  # خطا رخ داد
    progress_updated = pyqtSignal(int, int)  # (current, total)

    def __init__(self, llm_client: LLMClient, config: DebateConfig):
        super().__init__()
        self.llm_client = llm_client
        self.config = config
        self._is_running = True

    def run(self):
        try:
            debate_history: List[DebateTurn] = []
            total_turns = self.config.max_turns * 2  # هر طرف n نوبت

            # سیستم پرامپت‌های پایه
            base_system = f"""شما در یک مناظره هوش مصنوعی شرکت دارید.
موضوع مناظره: {self.config.topic}

قوانین:
- فقط متن صحبت خودتان را بنویسید
- از توضیحات اضافی، پیش‌درآمد یا پس‌درآمد خودداری کنید
- پاسخ باید طبیعی، استدلالی و متقاعدکننده باشد
- به طرف مقابل اشاره مستقیم نکنید، صحبت خودتان را بکنید
- پاسخ حداکثر ۳-۴ پاراگراف باشد"""

            for turn in range(total_turns):
                if not self._is_running:
                    break

                is_debater1_turn = turn % 2 == 0
                current_debater = self.config.debater1 if is_debater1_turn else self.config.debater2

                # ساخت پرامپت کاربر با توجه به تاریخچه
                user_prompt = self._build_prompt(current_debater, debate_history, turn)

                # ساخت سیستم پرامپت کامل
                system_prompt = f"""{base_system}

شخصیت شما: {current_debater.name}
{current_debater.prompt}"""

                # فراخوانی LLM
                response = self.llm_client.chat(system_prompt, user_prompt)

                # ایجاد نوبت
                debate_turn = DebateTurn(
                    speaker=current_debater.name,
                    content=response,
                    turn_number=turn + 1
                )

                debate_history.append(debate_turn)
                self.turn_generated.emit(debate_turn)
                self.progress_updated.emit(turn + 1, total_turns)

            # تولید نتیجه‌گیری مجری
            if self._is_running:
                conclusion = self._generate_conclusion(debate_history)
                self.debate_finished.emit(conclusion)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def _build_prompt(self, debater: Debater, history: List[DebateTurn], current_turn: int) -> str:
        """ساخت پرامپت کاربر با توجه به تاریخچه مناظره"""
        prompt_parts = [f"موضوع: {self.config.topic}\n"]
        prompt_parts.append(f"شما {debater.name} هستید.\n")

        if history:
            prompt_parts.append("مکالمات قبلی:\n")
            # فقط ۵ نوبت آخر رو بذار تا context کم نشه
            recent_history = history[-5:]
            for turn in recent_history:
                prompt_parts.append(f"{turn.speaker}: {turn.content}\n")

        prompt_parts.append(f"\nحالا نوبت شماست. لطفاً صحبت خودتان را انجام دهید:")
        return "\n".join(prompt_parts)

    def _generate_conclusion(self, history: List[DebateTurn]) -> str:
        """تولید نتیجه‌گیری توسط مجری"""
        # خلاصه مناظره برای مجری
        debate_summary = "\n\n".join([
            f"{turn.speaker}:\n{turn.content}"
            for turn in history
        ])

        moderator_system = f"""شما مجری و داور یک مناظره هوشمند هستید.
{self.config.moderator.prompt}

وظیفه شما:
1. تحلیل نقاط قوت و ضعف استدلال‌های طرفین
2. ارائه نتیجه‌گیری بی‌طرفانه
3. خلاصه‌ای از مباحث مطرح شده

فقط متن نتیجه‌گیری را بنویسید، بدون مقدمه."""

        moderator_user = f"""موضوع مناظره: {self.config.topic}

متن کامل مناظره:
{debate_summary}

لطفاً نتیجه‌گیری و تحلیل خود را ارائه دهید:"""

        return self.llm_client.chat(moderator_system, moderator_user, temperature=0.5)

    def stop(self):
        self._is_running = False
        self.wait(1000)


class DebateEngine:
    """
    فکتوری و کنترلر موتور مناظره
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self._current_thread: Optional[DebateEngineThread] = None

    def start_debate(self, config: DebateConfig,
                     on_turn: Callable,
                     on_finish: Callable,
                     on_error: Callable,
                     on_progress: Callable) -> DebateEngineThread:
        """
        شروع مناظره جدید

        Args:
            config: تنظیمات مناظره
            on_turn: callback برای هر نوبت
            on_finish: callback برای پایان
            on_error: callback برای خطا
            on_progress: callback برای پیشرفت

        Returns:
            آبجکت ترد مناظره
        """
        # لغو مناظره قبلی اگه وجود داره
        self.stop_debate()

        thread = DebateEngineThread(self.llm_client, config)
        thread.turn_generated.connect(on_turn)
        thread.debate_finished.connect(on_finish)
        thread.error_occurred.connect(on_error)
        thread.progress_updated.connect(on_progress)

        self._current_thread = thread
        thread.start()
        return thread

    def stop_debate(self):
        """توقف مناظره فعلی"""
        if self._current_thread and self._current_thread.isRunning():
            self._current_thread.stop()
            self._current_thread = None