# core/prompt_optimizer.py
from typing import Callable
from PyQt5.QtCore import QThread, pyqtSignal


class PromptOptimizerThread(QThread):
    """
    ترد برای بهینه‌سازی پرامپت بدون freeze کردن UI
    """
    optimized = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, llm_client, original_prompt: str, purpose: str):
        super().__init__()
        self.llm_client = llm_client
        self.original_prompt = original_prompt
        self.purpose = purpose

    def run(self):
        try:
            result = self.llm_client.optimize_prompt(self.original_prompt, self.purpose)
            self.optimized.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class PromptOptimizer:
    """
    کلاس فکتوری برای بهینه‌سازی پرامپت‌ها
    از الگوی Observer برای آپدیت UI استفاده می‌کنه
    """

    PURPOSE_DEBATER = "debater"
    PURPOSE_MODERATOR = "moderator"

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self._active_threads: list = []

    def optimize(self, original_prompt: str, purpose: str,
                 on_success: Callable, on_error: Callable) -> PromptOptimizerThread:
        """
        شروع بهینه‌سازی پرامپت در ترد جداگانه

        Args:
            original_prompt: پرامپت اصلی
            purpose: هدف پرامپت
            on_success: callback برای موفقیت
            on_error: callback برای خطا

        Returns:
            آبجکت ترد (برای کنترل)
        """
        thread = PromptOptimizerThread(self.llm_client, original_prompt, purpose)
        thread.optimized.connect(on_success)
        thread.error.connect(on_error)
        thread.finished.connect(lambda: self._cleanup_thread(thread))

        self._active_threads.append(thread)
        thread.start()
        return thread

    def _cleanup_thread(self, thread):
        if thread in self._active_threads:
            self._active_threads.remove(thread)

    def cancel_all(self):
        """لغو تمام عملیات فعال"""
        for thread in self._active_threads:
            thread.terminate()
        self._active_threads.clear()