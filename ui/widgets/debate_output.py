# ui/widgets/debate_output.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt
from core.debate_engine import DebateTurn


class DebateOutput(QWidget):
    """
    ویجت نمایش خروجی مناظره
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panel_frame")
        self._setup_ui()
        self._turns: list[DebateTurn] = []

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

        # تکست اریای خروجی
        self.output_text = QTextEdit()
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

        # فرمت نمایش
        text = f"\n{'=' * 60}\n"
        text += f"【 نوبت {turn.turn_number} | {turn.speaker} 】\n"
        text += f"{'=' * 60}\n\n"
        text += f"{turn.content}\n"

        self.output_text.append(text)
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )

    def set_conclusion(self, conclusion: str):
        """نمایش نتیجه‌گیری"""
        text = f"\n{'=' * 60}\n"
        text += f"【 نتیجه‌گیری مجری 】\n"
        text += f"{'=' * 60}\n\n"
        text += f"{conclusion}\n"

        self.output_text.append(text)
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