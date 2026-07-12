# ui/widgets/debater_card.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QPushButton, QGroupBox)
from PyQt5.QtCore import pyqtSignal


class DebaterCard(QGroupBox):
    """
    ویجت کارت مذاکره‌کننده
    شامل: نام، پرامپت، دکمه بهینه‌سازی
    """

    optimize_requested = pyqtSignal(str, str)  # (current_text, purpose)

    def __init__(self, title: str = "مذاکره‌کننده", parent=None):
        super().__init__(title, parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # ردیف نام
        name_layout = QHBoxLayout()
        name_label = QLabel("نام:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثلاً: ایلان ماسک")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input, 1)
        layout.addLayout(name_layout)

        # پرامپت
        prompt_label = QLabel("پرامپت شخصیت:")
        layout.addWidget(prompt_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "توضیحات شخصیت را اینجا بنویسید...\n"
            "مثال: شما ایلان ماسک هستید، مدیرعامل تسلا و اسپیس‌ایکس. "
            "دیدگاه مثبت به هوش مصنوعی دارید و معتقدید AI آینده بشریت را نجات می‌دهد."
        )
        self.prompt_input.setMinimumHeight(150)
        layout.addWidget(self.prompt_input)

        # دکمه بهینه‌سازی
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.optimize_btn = QPushButton("✨ بهینه‌سازی پرامپت")
        self.optimize_btn.setObjectName("optimize_btn")
        self.optimize_btn.setToolTip("با LLM پرامپت را حرفه‌ای کنید")
        self.optimize_btn.clicked.connect(self._on_optimize)
        btn_layout.addWidget(self.optimize_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _on_optimize(self):
        current_text = self.prompt_input.toPlainText().strip()
        if not current_text:
            self.prompt_input.setPlaceholderText("ابتدا پرامپتی بنویسید...")
            return

        purpose = "debater"
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.setText("⏳ در حال بهینه‌سازی...")
        self.optimize_requested.emit(current_text, purpose)

    def set_optimized_text(self, text: str):
        """پرامپت بهینه‌شده رو ست کن"""
        self.prompt_input.setPlainText(text)
        self.optimize_btn.setEnabled(True)
        self.optimize_btn.setText("✨ بهینه‌سازی پرامپت")

    def reset_optimize_button(self):
        self.optimize_btn.setEnabled(True)
        self.optimize_btn.setText("✨ بهینه‌سازی پرامپت")

    def get_data(self) -> tuple[str, str]:
        """دریافت نام و پرامپت"""
        return self.name_input.text().strip(), self.prompt_input.toPlainText().strip()

    def set_data(self, name: str, prompt: str):
        """ست کردن نام و پرامپت"""
        self.name_input.setText(name)
        self.prompt_input.setPlainText(prompt)