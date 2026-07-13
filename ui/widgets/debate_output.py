# ui/widgets/debate_output.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextBrowser, QPushButton, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt
from core.debate_engine import DebateTurn
import markdown2


class DebateOutput(QWidget):
    """
    ویجت نمایش خروجی مناظره
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panel_frame")
        self._setup_ui()
        self._turns: list[DebateTurn] = []
        self._stream_buffers: dict[int, str] = {}

    def _setup_ui(self):
        layout = QVBoxLayout()

        # هدر
        header = QHBoxLayout()
        header.addWidget(QLabel("📄 خروجی مناظره:"))
        header.addStretch()

        self.save_btn = QPushButton("💾 ذخیره فایل")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._on_save)
        header.addWidget(self.save_btn)

        self.clear_btn = QPushButton("🗑️ پاک کردن")
        self.clear_btn.clicked.connect(self._on_clear)
        header.addWidget(self.clear_btn)

        layout.addLayout(header)

        # پراگرس بار
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # تکست اریای خروجی (QTextBrowser برای رندر HTML/Markdown)
        self.output_text = QTextBrowser()
        self.output_text.setObjectName("output_area")
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText(
            "خروجی مناظره اینجا نمایش داده می‌شود...\n"
            "پس از اتمام، دکمه ذخیره را بزنید."
        )
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def add_turn(self, turn: DebateTurn):
        """اضافه کردن یک نوبت به خروجی"""
        self._turns.append(turn)

        # فرمت نمایش نهایی با تبدیل Markdown به HTML
        header = f"<hr><h3>نوبت {turn.turn_number} | {turn.speaker}</h3>"
        html = markdown2.markdown(turn.content)
        self.output_text.append(header + html)
        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())

        self.save_btn.setEnabled(True)

    def start_turn_stream(self, turn_number: int, speaker: str):
        """شروع بخش استریم برای یک نوبت جدید - اضافه کردن هدر اولیه"""
        header = f"<hr><h3>نوبت {turn_number} | {speaker}</h3>"
        self.output_text.append(header)
        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())

    def append_turn_chunk(self, turn_number: int, chunk: str):
        """افزودن chunk جریان متنی: ذخیره و نمایش متن خام تا تکمیل نوبت"""
        if not chunk:
            return
        if turn_number not in self._stream_buffers:
            self._stream_buffers[turn_number] = ""
        self._stream_buffers[turn_number] += chunk
        self.output_text.insertPlainText(chunk)
        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())

    def finalize_streamed_turn(self, turn: DebateTurn):
        """وقتی نوبت کامل شد، متن کامل را به صورت Markdown رندر می‌کند."""
        self._stream_buffers.pop(turn.turn_number, None)
        if not any(existing.turn_number == turn.turn_number for existing in self._turns):
            self._turns.append(turn)
        self._render_all_turns()
        self.save_btn.setEnabled(True)

    def _render_all_turns(self):
        self.output_text.clear()
        for turn in self._turns:
            header = f"<hr><h3>نوبت {turn.turn_number} | {turn.speaker}</h3>"
            html = markdown2.markdown(turn.content)
            self.output_text.append(header + html)
        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())

    def set_conclusion(self, conclusion: str):
        """نمایش نتیجه‌گیری"""
        header = f"<hr><h2>نتیجه‌گیری مجری</h2>"
        html = markdown2.markdown(conclusion)
        self.output_text.append(header + html)
        self.save_btn.setEnabled(True)
        self.progress.setVisible(False)

    def set_progress(self, current: int, total: int):
        """آپدیت پراگرس بار"""
        self.progress.setVisible(True)
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.progress.setFormat(f"در حال تولید... {current}/{total}")

    def reset(self):
        """ریست کردن خروجی"""
        self._turns.clear()
        self.output_text.clear()
        self.save_btn.setEnabled(False)
        self.progress.setVisible(False)

    def get_full_text(self) -> str:
        """دریافت متن کامل"""
        return self.output_text.toPlainText()

    def get_turns(self) -> list[DebateTurn]:
        return self._turns.copy()

    def _on_clear(self):
        self.reset()

    def _on_save(self):
        self.save_btn.setEnabled(False)
        # سیگنال به والد برای ذخیره
        # اینجا فقط UI رو آپدیت می‌کنیم