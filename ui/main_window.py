# ui/main_window.py
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QSpinBox, QPushButton,
                             QMessageBox, QFileDialog, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
from config import WINDOW_WIDTH, WINDOW_HEIGHT, MAX_TURNS_DEFAULT
from core.llm_client import LLMClient
from core.prompt_optimizer import PromptOptimizer
from core.debate_engine import DebateEngine
from models.debate_config import DebateConfig
from models.debate_project import DebateProject
from models.debater import Debater
from ui.styles import DARK_THEME
from ui.widgets.debater_card import DebaterCard
from ui.widgets.moderator_card import ModeratorCard
from ui.widgets.debate_output import DebateOutput
from utils.file_handler import FileHandler
from core.debate_engine import DebateTurn


class MainWindow(QMainWindow):
    """
    پنجره اصلی اپلیکیشن - Controller در الگوی MVC
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎭 DebateAI - پلتفرم مناظره هوشمند")

        screen = QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            self.setMinimumSize(
                min(WINDOW_WIDTH, available.width()),
                min(WINDOW_HEIGHT, available.height())
            )
        else:
            self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Initialize core components
        self.llm_client = LLMClient()
        self.prompt_optimizer = PromptOptimizer(self.llm_client)
        self.debate_engine = DebateEngine(self.llm_client)

        # State
        self._current_debate_data = {
            'topic': '',
            'debater1_name': '', 'debater1_prompt': '',
            'debater2_name': '', 'debater2_prompt': '',
            'moderator_name': '', 'moderator_prompt': '',
            'turns': [],
            'conclusion': ''
        }

        self._setup_ui()
        self.setStyleSheet(DARK_THEME)
        self.showMaximized()
        # track active streaming turns to initialize headers once
        self._active_streaming_turns = set()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === ستون چپ: تنظیمات ===
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(440)
        left_scroll.setMaximumWidth(520)
        left_scroll.setFrameShape(QFrame.NoFrame)

        left_widget = QWidget()
        left_widget.setObjectName("panel_frame")
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(18, 18, 18, 18)

        # عنوان
        title = QLabel("🎭 DebateAI")
        title.setStyleSheet("font-size: 24px; color: #e94560;")
        left_layout.addWidget(title)

        # موضوع
        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("موضوع مناظره:"))
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("مثلاً: آینده هوش مصنوعی در مشاغل")
        topic_layout.addWidget(self.topic_input)
        left_layout.addLayout(topic_layout)

        # تعداد نوبت‌ها
        turns_layout = QHBoxLayout()
        turns_layout.addWidget(QLabel("تعداد نوبت (هر طرف):"))
        self.turns_spin = QSpinBox()
        self.turns_spin.setRange(1, 100)
        self.turns_spin.setValue(MAX_TURNS_DEFAULT)
        self.turns_spin.setSuffix(" نوبت")
        turns_layout.addWidget(self.turns_spin)
        turns_layout.addStretch()
        left_layout.addLayout(turns_layout)

        # کارت‌های مذاکره‌کننده‌ها
        self.debater1_card = DebaterCard("🥊 طرف اول مناظره")
        self.debater1_card.optimize_requested.connect(self._on_optimize_prompt)
        left_layout.addWidget(self.debater1_card)

        self.debater2_card = DebaterCard("🛡️ طرف دوم مناظره")
        self.debater2_card.optimize_requested.connect(self._on_optimize_prompt)
        left_layout.addWidget(self.debater2_card)

        # کارت مجری
        self.moderator_card = ModeratorCard()
        self.moderator_card.optimize_requested.connect(self._on_optimize_prompt)
        left_layout.addWidget(self.moderator_card)

        # دکمه‌های کنترل
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ شروع مناظره")
        self.start_btn.setObjectName("start_btn")
        self.start_btn.clicked.connect(self._on_start_debate)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ توقف")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop_debate)
        btn_layout.addWidget(self.stop_btn)

        left_layout.addLayout(btn_layout)

        # دکمه‌های ذخیره و بارگذاری پروژه
        project_btn_layout = QHBoxLayout()

        self.save_project_btn = QPushButton("💾 ذخیره پروژه")
        self.save_project_btn.setObjectName("save_btn")
        self.save_project_btn.clicked.connect(self._on_save_project)
        project_btn_layout.addWidget(self.save_project_btn)

        self.load_project_btn = QPushButton("📂 بارگذاری پروژه")
        self.load_project_btn.setObjectName("load_btn")
        self.load_project_btn.clicked.connect(self._on_load_project)
        project_btn_layout.addWidget(self.load_project_btn)

        left_layout.addLayout(project_btn_layout)

        left_layout.addLayout(btn_layout)

        # API Key
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("🔑 API Key:"))
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("OpenAI API Key (اختیاری)")
        self.api_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.api_input)
        left_layout.addLayout(api_layout)

        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        left_scroll.setWidget(left_widget)

        main_layout.addWidget(left_scroll)

        # === ستون راست: خروجی ===
        self.output_widget = DebateOutput()
        self.output_widget.setObjectName("panel_frame")
        self.output_widget.setMinimumWidth(700)
        self.output_widget.save_btn.clicked.connect(self._on_save_file)
        main_layout.addWidget(self.output_widget, stretch=1)

        central.setLayout(main_layout)

    def _on_optimize_prompt(self, text: str, purpose: str):
        """هندل بهینه‌سازی پرامپت"""
        # پیدا کردن کارت فرستنده
        sender = self.sender()

        def on_success(optimized: str):
            sender.set_optimized_text(optimized)
            QMessageBox.information(self, "✅ موفق", "پرامپت با موفقیت بهینه شد!")

        def on_error(error: str):
            sender.reset_optimize_button()
            QMessageBox.critical(self, "❌ خطا", f"خطا در بهینه‌سازی:\n{error}")

        self.prompt_optimizer.optimize(text, purpose, on_success, on_error)

    def _on_start_debate(self):
        """شروع مناظره"""
        # اعتبارسنجی
        topic = self.topic_input.text().strip()
        d1_name, d1_prompt = self.debater1_card.get_data()
        d2_name, d2_prompt = self.debater2_card.get_data()
        mod_name, mod_prompt = self.moderator_card.get_data()

        config = DebateConfig(
            topic=topic,
            debater1=Debater(name=d1_name, prompt=d1_prompt),
            debater2=Debater(name=d2_name, prompt=d2_prompt),
            moderator=Debater(name=mod_name, prompt=mod_prompt, role="moderator"),
            max_turns=self.turns_spin.value()
        )

        valid, msg = config.validate()
        if not valid:
            QMessageBox.warning(self, "⚠️ اعتبارسنجی", msg)
            return

        # آپدیت API key اگه وارد شده
        api_key = self.api_input.text().strip()
        if api_key:
            self.llm_client.api_key = api_key

        # ذخیره داده‌ها برای export
        self._current_debate_data.update({
            'topic': topic,
            'debater1_name': d1_name, 'debater1_prompt': d1_prompt,
            'debater2_name': d2_name, 'debater2_prompt': d2_prompt,
            'moderator_name': mod_name, 'moderator_prompt': mod_prompt,
        })

        # UI آپدیت
        self.output_widget.reset()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # شروع موتور
        self.debate_engine.start_debate(
            config=config,
            on_turn=self._on_turn_generated,
            on_finish=self._on_debate_finished,
            on_error=self._on_debate_error,
            on_progress=self._on_progress_updated,
            on_chunk=self._on_turn_chunk,
            on_conclusion_chunk=self._on_conclusion_chunk
        )

    def _on_stop_debate(self):
        """توقف مناظره"""
        self.debate_engine.stop_debate()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


    def _on_turn_generated(self, turn: DebateTurn):
        """هر نوبت تولید شد"""
        self._current_debate_data['turns'].append(turn)
        if turn.turn_number in self._active_streaming_turns:
            self.output_widget.finalize_streamed_turn(turn)
            self._active_streaming_turns.discard(turn.turn_number)
            return
        self.output_widget.add_turn(turn)

    def _on_turn_chunk(self, turn_number: int, chunk: str):
        """هندل هر chunk برای یک نوبت: اطمینان از هدر و درج جزئی"""
        if turn_number not in self._active_streaming_turns:
            # اولین chunk برای این نوبت: اضافه کردن هدر
            # speaker unknown here, rely on turn_number ordering
            # attempt to map to debater names: odd/even
            if turn_number % 2 == 1:
                speaker = self._current_debate_data.get('debater1_name', 'طرف اول')
            else:
                speaker = self._current_debate_data.get('debater2_name', 'طرف دوم')
            self.output_widget.start_turn_stream(turn_number, speaker)
            self._active_streaming_turns.add(turn_number)

        # append the chunk to the UI
        self.output_widget.append_turn_chunk(turn_number, chunk)

    def _on_conclusion_chunk(self, chunk: str):
        """هندل chunkهای نتیجه‌گیری مجری (streaming)"""
        self.output_widget.append_turn_chunk(0, chunk)

    def _on_debate_finished(self, conclusion: str):
        """مناظره تموم شد"""
        self._current_debate_data['conclusion'] = conclusion
        self.output_widget.set_conclusion(conclusion)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        QMessageBox.information(self, "✅ تمام شد",
                                "مناظره با موفقیت تولید شد!\nمی‌توانید فایل را ذخیره کنید.")

    def _on_debate_error(self, error: str):
        """خطا در مناظره"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, "❌ خطا", f"خطا در تولید مناظره:\n{error}")

    def _on_progress_updated(self, current: int, total: int):
        """آپدیت پیشرفت"""
        self.output_widget.set_progress(current, total)

    def _on_save_file(self):
        """ذخیره فایل Markdown"""
        try:
            filepath = FileHandler.export_debate(
                topic=self._current_debate_data['topic'],
                debater1_name=self._current_debate_data['debater1_name'],
                debater1_prompt=self._current_debate_data['debater1_prompt'],
                debater2_name=self._current_debate_data['debater2_name'],
                debater2_prompt=self._current_debate_data['debater2_prompt'],
                moderator_name=self._current_debate_data['moderator_name'],
                moderator_prompt=self._current_debate_data['moderator_prompt'],
                turns=self._current_debate_data['turns'],
                conclusion=self._current_debate_data['conclusion']
            )

            QMessageBox.information(self, "✅ ذخیره شد",
                                    f"فایل با موفقیت ذخیره شد:\n{filepath}")

        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در ذخیره فایل:\n{str(e)}")

    def _on_save_project(self):
        """ذخیره پروژه به فایل JSON"""
        try:
            config = DebateConfig(
                topic=self.topic_input.text().strip(),
                debater1=Debater(name=self.debater1_card.name_input.text().strip(),
                                 prompt=self.debater1_card.prompt_input.toPlainText().strip()),
                debater2=Debater(name=self.debater2_card.name_input.text().strip(),
                                 prompt=self.debater2_card.prompt_input.toPlainText().strip()),
                moderator=Debater(name=self.moderator_card.name_input.text().strip(),
                                  prompt=self.moderator_card.prompt_input.toPlainText().strip(),
                                  role="moderator"),
                max_turns=self.turns_spin.value()
            )

            project = DebateProject(
                config=config,
                turns=self._current_debate_data['turns'],
                conclusion=self._current_debate_data['conclusion']
            )

            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "ذخیره پروژه مناظره",
                "projects",
                "JSON Files (*.json);;All Files (*)"
            )

            if filepath:
                FileHandler.save_project_json(project, filepath)
                QMessageBox.information(self, "✅ ذخیره شد", f"پروژه ذخیره شد:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در ذخیره پروژه:\n{str(e)}")

    def _on_load_project(self):
        """بارگذاری پروژه از فایل JSON"""
        try:
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "بارگذاری پروژه مناظره",
                "projects",
                "JSON Files (*.json);;All Files (*)"
            )

            if filepath:
                project = FileHandler.load_project_json(filepath)

                # آپدیت UI
                self.topic_input.setText(project.config.topic)
                self.turns_spin.setValue(project.config.max_turns)

                self.debater1_card.name_input.setText(project.config.debater1.name)
                self.debater1_card.prompt_input.setPlainText(project.config.debater1.prompt)

                self.debater2_card.name_input.setText(project.config.debater2.name)
                self.debater2_card.prompt_input.setPlainText(project.config.debater2.prompt)

                self.moderator_card.name_input.setText(project.config.moderator.name)
                self.moderator_card.prompt_input.setPlainText(project.config.moderator.prompt)

                # بارگذاری نتایج
                self.output_widget.reset()
                if project.turns:
                    for turn in project.turns:
                        self.output_widget.add_turn(turn)
                if project.conclusion:
                    self.output_widget.set_conclusion(project.conclusion)

                # آپدیت state
                self._current_debate_data.update({
                    'topic': project.config.topic,
                    'debater1_name': project.config.debater1.name,
                    'debater1_prompt': project.config.debater1.prompt,
                    'debater2_name': project.config.debater2.name,
                    'debater2_prompt': project.config.debater2.prompt,
                    'moderator_name': project.config.moderator.name,
                    'moderator_prompt': project.config.moderator.prompt,
                    'turns': project.turns,
                    'conclusion': project.conclusion
                })

                QMessageBox.information(self, "✅ بارگذاری شد", f"پروژه بارگذاری شد:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در بارگذاری پروژه:\n{str(e)}")


    def closeEvent(self, event):
        """بستن اپلیکیشن"""
        self.debate_engine.stop_debate()
        self.prompt_optimizer.cancel_all()
        event.accept()