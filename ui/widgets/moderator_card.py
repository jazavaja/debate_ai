# ui/widgets/moderator_card.py
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton)
from ui.widgets.debater_card import DebaterCard


class ModeratorCard(DebaterCard):
    """
    ویجت کارت داور/مجری - ارث‌بری از DebaterCard
    """

    def __init__(self, parent=None):
        super().__init__("🎙️ مجری و داور مناظره", parent)
        self._customize_ui()

    def _customize_ui(self):
        # تغییر placeholder
        self.name_input.setPlaceholderText("مثلاً: دکتر علی رضایی")
        self.prompt_input.setPlaceholderText(
            "شخصیت مجری را توصیف کنید...\n"
            "مثال: شما یک استاد دانشگاه و کارشناس بی‌طرف در حوزه فناوری هستید. "
            "تخصص شما تحلیل مناظرات و ارائه نتیجه‌گیری‌های منطقی است. "
            "لحن شما جدی، تحلیلی و بی‌طرفانه است."
        )
        self.optimize_btn.setText("✨ بهینه‌سازی مجری")

    def _on_optimize(self):
        current_text = self.prompt_input.toPlainText().strip()
        if not current_text:
            return

        purpose = "moderator"
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.setText("⏳ در حال بهینه‌سازی...")
        self.optimize_requested.emit(current_text, purpose)