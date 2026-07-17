# core/prompt_optimizer.py
from typing import Callable
from PyQt5.QtCore import QThread, pyqtSignal


class PromptOptimizerThread(QThread):
    """
    ترد برای بهینه‌سازی پرامپت بدون freeze کردن UI
    """
    chunk = pyqtSignal(str)  # برای streaming چانک‌ها
    optimized = pyqtSignal(str)  # برای نتیجه نهایی (backward compatibility)
    error = pyqtSignal(str)

    def __init__(self, llm_client, original_prompt: str, purpose: str, name: str = "", use_stream: bool = True):
        super().__init__()
        self.llm_client = llm_client
        self.original_prompt = original_prompt
        self.purpose = purpose
        self.name = name
        self.use_stream = use_stream

    def run(self):
        try:
            if self.use_stream:
                # استفاده از streaming
                final_text = ""
                
                def on_chunk(text):
                    nonlocal final_text
                    final_text += text
                    self.chunk.emit(text)
                
                self.llm_client.optimize_prompt_stream(
                    self.original_prompt, 
                    self.purpose, 
                    on_chunk, 
                    name=self.name,
                    temperature=0.3
                )
                self.optimized.emit(final_text)
            else:
                # روش قدیمی بدون streaming
                result = self.llm_client.optimize_prompt(self.original_prompt, self.purpose, self.name)
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

    def optimize(self, original_prompt: str, purpose: str, name: str = "",
                 on_chunk: Callable = None, on_success: Callable = None, on_error: Callable = None,
                 use_stream: bool = True) -> PromptOptimizerThread:
        """
        شروع بهینه‌سازی پرامپت در ترد جداگانه

        Args:
            original_prompt: پرامپت اصلی
            purpose: هدف پرامپت
            name: نام شخصیت
            on_chunk: callback برای دریافت چانک‌های streaming
            on_success: callback برای موفقیت
            on_error: callback برای خطا
            use_stream: استفاده از streaming یا روش قدیمی

        Returns:
            آبجکت ترد (برای کنترل)
        """
        thread = PromptOptimizerThread(self.llm_client, original_prompt, purpose, name, use_stream)
        
        if on_chunk:
            thread.chunk.connect(on_chunk)
        
        if on_success:
            thread.optimized.connect(on_success)
        
        if on_error:
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