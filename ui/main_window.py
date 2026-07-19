# ui/main_window.py
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton,
    QFileDialog, QScrollArea, QFrame,
)
from PyQt5.QtCore import Qt
from config import WINDOW_WIDTH, WINDOW_HEIGHT, MAX_TURNS_DEFAULT
from core.llm_client import LLMClient
from core.prompt_optimizer import PromptOptimizer
from core.debate_engine import DebateEngine
from models.debate_config import DebateConfig
from models.debate_project import DebateProject
from models.debate_status import DebateStatus, GenerationError
from models.debate_turn import DebateTurn
from models.debater import Debater
from ui.styles import DARK_THEME
from ui.custom_messagebox import CustomMessageBox
from ui.widgets.debater_card import DebaterCard
from ui.widgets.moderator_card import ModeratorCard
from ui.widgets.debate_output import DebateOutput
from utils.file_handler import FileHandler


class MainWindow(QMainWindow):
    """پنجره اصلی اپلیکیشن - Controller در الگوی MVC."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎭 DebateAI - پلتفرم مناظره هوشمند")

        screen = QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            self.setMinimumSize(
                min(WINDOW_WIDTH, available.width()),
                min(WINDOW_HEIGHT, available.height()),
            )
        else:
            self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.llm_client = LLMClient()
        self.prompt_optimizer = PromptOptimizer(self.llm_client)
        self.debate_engine = DebateEngine(self.llm_client)

        self._current_debate_data = {
            "topic": "",
            "debater1_name": "", "debater1_prompt": "",
            "debater2_name": "", "debater2_prompt": "",
            "moderator_name": "", "moderator_prompt": "",
            "turns": [],
            "conclusion": "",
            "status": DebateStatus.PENDING,
            "generation_error": None,
        }

        self._setup_ui()
        self.setStyleSheet(DARK_THEME)
        self.showMaximized()
        self._active_streaming_turns: dict[int, str] = {}

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(580)
        left_scroll.setMaximumWidth(700)
        left_scroll.setFrameShape(QFrame.NoFrame)

        left_widget = QWidget()
        left_widget.setObjectName("panel_frame")
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(18, 18, 18, 18)

        title = QLabel("🎭 DebateAI")
        title.setStyleSheet("font-size: 24px; color: #e94560;")
        left_layout.addWidget(title)

        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("موضوع مناظره:"))
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("مثلاً: آینده هوش مصنوعی در مشاغل")
        topic_layout.addWidget(self.topic_input)
        left_layout.addLayout(topic_layout)

        turns_layout = QHBoxLayout()
        turns_layout.addWidget(QLabel("تعداد نوبت (هر طرف):"))
        self.turns_spin = QSpinBox()
        self.turns_spin.setRange(1, 100)
        self.turns_spin.setValue(MAX_TURNS_DEFAULT)
        self.turns_spin.setSuffix(" نوبت")
        turns_layout.addWidget(self.turns_spin)
        turns_layout.addStretch()
        left_layout.addLayout(turns_layout)

        self.debater1_card = DebaterCard("🥊 طرف اول مناظره")
        self.debater1_card.optimize_requested.connect(self._on_optimize_prompt)
        left_layout.addWidget(self.debater1_card)

        self.debater2_card = DebaterCard("🛡️ طرف دوم مناظره")
        self.debater2_card.optimize_requested.connect(self._on_optimize_prompt)
        left_layout.addWidget(self.debater2_card)

        self.moderator_card = ModeratorCard()
        self.moderator_card.optimize_requested.connect(self._on_optimize_prompt)
        left_layout.addWidget(self.moderator_card)

        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ شروع مناظره")
        self.start_btn.setObjectName("start_btn")
        self.start_btn.clicked.connect(self._on_start_debate)
        btn_layout.addWidget(self.start_btn)

        self.resume_btn = QPushButton("⏩ ادامه مناظره")
        self.resume_btn.setObjectName("resume_btn")
        self.resume_btn.setEnabled(False)
        self.resume_btn.clicked.connect(self._on_resume_debate)
        btn_layout.addWidget(self.resume_btn)

        self.stop_btn = QPushButton("⏹️ توقف")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop_debate)
        btn_layout.addWidget(self.stop_btn)

        left_layout.addLayout(btn_layout)

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

        self.output_widget = DebateOutput()
        self.output_widget.setObjectName("panel_frame")
        self.output_widget.setMinimumWidth(700)
        self.output_widget.save_btn.clicked.connect(self._on_save_file)
        self.output_widget.clear_btn.clicked.connect(self._on_clear_output)
        main_layout.addWidget(self.output_widget, stretch=1)

        central.setLayout(main_layout)

    # ------------------------------------------------------------------ #
    # Config helpers
    # ------------------------------------------------------------------ #

    def _build_config(self) -> DebateConfig:
        d1_name, d1_prompt = self.debater1_card.get_data()
        d2_name, d2_prompt = self.debater2_card.get_data()
        mod_name, mod_prompt = self.moderator_card.get_data()
        return DebateConfig(
            topic=self.topic_input.text().strip(),
            debater1=Debater(name=d1_name, prompt=d1_prompt),
            debater2=Debater(name=d2_name, prompt=d2_prompt),
            moderator=Debater(name=mod_name, prompt=mod_prompt, role="moderator"),
            max_turns=self.turns_spin.value(),
        )

    def _apply_api_key(self):
        api_key = self.api_input.text().strip()
        if api_key:
            self.llm_client.api_key = api_key

    def _set_generation_ui(self, running: bool):
        self.start_btn.setEnabled(not running)
        self.resume_btn.setEnabled(not running and self._can_resume())
        self.stop_btn.setEnabled(running)

    def _can_resume(self) -> bool:
        status = self._current_debate_data.get("status", DebateStatus.PENDING)
        turns = self._current_debate_data.get("turns", [])
        conclusion = self._current_debate_data.get("conclusion", "")
        if status == DebateStatus.COMPLETED:
            return False
        if status in (DebateStatus.FAILED, DebateStatus.STOPPED):
            return True
        if turns and not conclusion:
            return True
        return False

    def _build_debate_markdown(self) -> str:
        """ساخت محتوای Markdown برای ذخیره فایل"""
        from datetime import datetime
        from models.debate_status import TurnType
        
        topic = self._current_debate_data["topic"]
        debater1_name = self._current_debate_data["debater1_name"]
        debater1_prompt = self._current_debate_data["debater1_prompt"]
        debater2_name = self._current_debate_data["debater2_name"]
        debater2_prompt = self._current_debate_data["debater2_prompt"]
        moderator_name = self._current_debate_data["moderator_name"]
        moderator_prompt = self._current_debate_data["moderator_prompt"]
        turns = self._current_debate_data["turns"]
        conclusion = self._current_debate_data["conclusion"]
        
        lines = [
            f"# مناظره: {topic}",
            "",
            f"**تاریخ:** {datetime.now().strftime('%Y/%m/%d %H:%M')}",
            f"**تعداد نوبت‌ها:** {len(turns)}",
            "",
            "---",
            "",
            "## معرفی مجری",
            "",
            f"**{moderator_name}**",
            "",
            f"{moderator_prompt}",
            "",
            "---",
            "",
            "## معرفی طرفین مناظره",
            "",
            f"### {debater1_name}",
            "",
            f"{debater1_prompt}",
            "",
            f"### {debater2_name}",
            "",
            f"{debater2_prompt}",
            "",
            "---",
            "",
            "## متن کامل مناظره",
            "",
        ]
        
        # اضافه کردن مکالمات
        for turn in turns:
            if turn.turn_type == TurnType.MODERATOR_INTRO:
                section = f"### 🎙️ معرفی مجری: {turn.speaker}"
            elif turn.turn_type == TurnType.MODERATOR_INTERVENTION:
                section = f"### 🎙️ مداخله مجری: {turn.speaker}"
            else:
                section = f"### نوبت {turn.turn_number}: {turn.speaker}"
            lines.append(section)
            lines.append("")
            lines.append(turn.content)
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # نتیجه‌گیری
        lines.extend([
            "",
            "## نتیجه‌گیری و تحلیل مجری",
            "",
            f"**{moderator_name}:**",
            "",
            conclusion,
            "",
            "---",
            "",
            "*تولید شده توسط DebateAI*",
        ])
        
        return "\n".join(lines)

    def _start_engine(self, resume: bool = False):
        config = self._build_config()
        valid, msg = config.validate()
        if not valid:
            CustomMessageBox.warning(self, "⚠️ اعتبارسنجی", msg)
            return

        self._apply_api_key()
        self._set_generation_ui(running=True)
        self._active_streaming_turns.clear()

        if not resume:
            self.output_widget.reset()
            self._current_debate_data["turns"] = []
            self._current_debate_data["conclusion"] = ""
            self._current_debate_data["generation_error"] = None

        self._current_debate_data.update({
            "topic": config.topic,
            "debater1_name": config.debater1.name,
            "debater1_prompt": config.debater1.prompt,
            "debater2_name": config.debater2.name,
            "debater2_prompt": config.debater2.prompt,
            "moderator_name": config.moderator.name,
            "moderator_prompt": config.moderator.prompt,
        })

        existing_turns = list(self._current_debate_data["turns"]) if resume else []
        existing_conclusion = self._current_debate_data.get("conclusion", "") if resume else ""

        self.debate_engine.start_debate(
            config=config,
            on_turn=self._on_turn_generated,
            on_finish=self._on_debate_finished,
            on_error=self._on_debate_error,
            on_progress=self._on_progress_updated,
            on_chunk=self._on_turn_chunk,
            on_conclusion_chunk=self._on_conclusion_chunk,
            on_stream_start=self._on_turn_stream_start,
            on_status_changed=self._on_status_changed,
            existing_turns=existing_turns,
            existing_conclusion=existing_conclusion,
            resume=resume,
        )

    # ------------------------------------------------------------------ #
    # Event handlers
    # ------------------------------------------------------------------ #

    def _on_optimize_prompt(self, text: str, purpose: str, name: str = ""):
        sender = self.sender()
        streaming_started = False

        def on_chunk(chunk: str):
            nonlocal streaming_started
            if not chunk:
                return
            if not streaming_started:
                sender.begin_optimized_stream()
                streaming_started = True
            sender.append_optimized_chunk(chunk)

        def on_success(final_text: str):
            if streaming_started:
                sender.finish_optimized_stream()
            elif final_text.strip():
                sender.set_optimized_text(final_text)
            else:
                sender.reset_optimize_button()
                CustomMessageBox.warning(self, "⚠️ خطا", "پاسخی از مدل دریافت نشد.")
                return
            CustomMessageBox.information(self, "✅ موفق", "پرامپت با موفقیت بهینه شد!")

        def on_error(error: str):
            if streaming_started:
                sender.finish_optimized_stream()
            else:
                sender.reset_optimize_button()
            CustomMessageBox.critical(self, "❌ خطا", f"خطا در بهینه‌سازی:\n{error}")

        self.prompt_optimizer.optimize(
            text,
            purpose,
            name=name,
            on_chunk=on_chunk,
            on_success=on_success,
            on_error=on_error,
            use_stream=True,
        )

    def _on_start_debate(self):
        self._start_engine(resume=False)

    def _on_resume_debate(self):
        if not self._can_resume():
            CustomMessageBox.information(self, "ℹ️", "مناظره‌ای برای ادامه وجود ندارد.")
            return
        self._start_engine(resume=True)

    def _on_stop_debate(self):
        self.debate_engine.stop_debate()
        self._current_debate_data["status"] = DebateStatus.STOPPED
        self.output_widget.set_status(DebateStatus.STOPPED)
        self._set_generation_ui(running=False)

    def _on_turn_stream_start(self, turn_number: int, speaker: str, turn_type: str):
        self._active_streaming_turns[turn_number] = turn_type
        self.output_widget.start_turn_stream(turn_number, speaker, turn_type)

    def _on_turn_generated(self, turn: DebateTurn):
        self._current_debate_data["turns"].append(turn)
        if turn.turn_number in self._active_streaming_turns:
            self.output_widget.finalize_streamed_turn(turn)
            del self._active_streaming_turns[turn.turn_number]
            return
        self.output_widget.add_turn(turn)

    def _on_turn_chunk(self, turn_number: int, chunk: str):
        self.output_widget.append_turn_chunk(turn_number, chunk)

    def _on_conclusion_chunk(self, chunk: str):
        self.output_widget.append_conclusion_chunk(chunk)

    def _on_debate_finished(self, conclusion: str):
        self._current_debate_data["conclusion"] = conclusion
        self._current_debate_data["status"] = DebateStatus.COMPLETED
        self._current_debate_data["generation_error"] = None
        self.output_widget.set_conclusion(conclusion)
        self.output_widget.set_status(DebateStatus.COMPLETED)
        self._set_generation_ui(running=False)
        CustomMessageBox.information(
            self, "✅ تمام شد",
            "مناظره با موفقیت تولید شد!\nمی‌توانید فایل را ذخیره کنید.",
        )

    def _on_debate_error(self, error: GenerationError):
        self._current_debate_data["status"] = DebateStatus.FAILED
        self._current_debate_data["generation_error"] = error
        self.output_widget.set_status(DebateStatus.FAILED, error.message)
        self._set_generation_ui(running=False)
        CustomMessageBox.critical(
            self, "❌ تولید متوقف شد",
            f"تولید مناظره متوقف شد.\n\n"
            f"مرحله: {error.step}\n"
            f"خطا: {error.message}\n\n"
            f"می‌توانید پروژه را ذخیره کرده و بعداً «ادامه مناظره» را بزنید.",
        )

    def _on_status_changed(self, status_value: str):
        try:
            status = DebateStatus(status_value)
        except ValueError:
            return
        self._current_debate_data["status"] = status
        self.output_widget.set_status(status)

    def _on_progress_updated(self, current: int, total: int):
        self.output_widget.set_progress(current, total)

    def _on_clear_output(self):
        self.output_widget.reset()
        self._current_debate_data["turns"] = []
        self._current_debate_data["conclusion"] = ""
        self._current_debate_data["status"] = DebateStatus.PENDING
        self._current_debate_data["generation_error"] = None
        self.resume_btn.setEnabled(False)

    def _on_save_file(self):
        try:
            # نمایش dialog برای انتخاب مسیر ذخیره
            default_filename = f"debate_{self._current_debate_data['topic'].replace(' ', '_')}.md"
            filepath, _ = QFileDialog.getSaveFileName(
                self, "ذخیره مناظره", default_filename,
                "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)",
            )
            
            if not filepath:
                return
            
            # ذخیره فایل در مسیر انتخاب شده
            content = self._build_debate_markdown()
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            CustomMessageBox.information(self, "✅ ذخیره شد", f"فایل با موفقیت ذخیره شد:\n{filepath}")
        except Exception as e:
            CustomMessageBox.critical(self, "❌ خطا", f"خطا در ذخیره فایل:\n{str(e)}")

    def _on_save_project(self):
        try:
            project = DebateProject(
                config=self._build_config(),
                turns=self._current_debate_data["turns"],
                conclusion=self._current_debate_data["conclusion"],
                status=self._current_debate_data.get("status", DebateStatus.PENDING),
                generation_error=self._current_debate_data.get("generation_error"),
            )

            filepath, _ = QFileDialog.getSaveFileName(
                self, "ذخیره پروژه مناظره", "projects",
                "JSON Files (*.json);;All Files (*)",
            )
            if filepath:
                FileHandler.save_project_json(project, filepath)
                CustomMessageBox.information(self, "✅ ذخیره شد", f"پروژه ذخیره شد:\n{filepath}")
        except Exception as e:
            CustomMessageBox.critical(self, "❌ خطا", f"خطا در ذخیره پروژه:\n{str(e)}")

    def _on_load_project(self):
        try:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "بارگذاری پروژه مناظره", "projects",
                "JSON Files (*.json);;All Files (*)",
            )
            if not filepath:
                return

            project = FileHandler.load_project_json(filepath)

            self.topic_input.setText(project.config.topic)
            self.turns_spin.setValue(project.config.max_turns)
            self.debater1_card.name_input.setText(project.config.debater1.name)
            self.debater1_card.prompt_input.setPlainText(project.config.debater1.prompt)
            self.debater2_card.name_input.setText(project.config.debater2.name)
            self.debater2_card.prompt_input.setPlainText(project.config.debater2.prompt)
            self.moderator_card.name_input.setText(project.config.moderator.name)
            self.moderator_card.prompt_input.setPlainText(project.config.moderator.prompt)

            self.output_widget.reset()
            if project.turns:
                for turn in project.turns:
                    self.output_widget.add_turn(turn)
            if project.conclusion:
                self.output_widget.set_conclusion(project.conclusion)

            status = project.status
            if project.turns and not project.conclusion and status == DebateStatus.PENDING:
                status = DebateStatus.STOPPED

            error_msg = project.generation_error.message if project.generation_error else ""
            self.output_widget.set_status(status, error_msg)

            self._current_debate_data.update({
                "topic": project.config.topic,
                "debater1_name": project.config.debater1.name,
                "debater1_prompt": project.config.debater1.prompt,
                "debater2_name": project.config.debater2.name,
                "debater2_prompt": project.config.debater2.prompt,
                "moderator_name": project.config.moderator.name,
                "moderator_prompt": project.config.moderator.prompt,
                "turns": project.turns,
                "conclusion": project.conclusion,
                "status": status,
                "generation_error": project.generation_error,
            })

            self.resume_btn.setEnabled(project.is_resumable())
            self._set_generation_ui(running=False)

            msg = f"پروژه بارگذاری شد:\n{filepath}"
            if project.is_resumable():
                debater_done = project.debater_turns_completed()
                total = project.config.max_turns * 2
                msg += f"\n\n{debater_done}/{total} نوبت تولید شده."
                msg += "\nبرای ادامه، «⏩ ادامه مناظره» را بزنید."
            CustomMessageBox.information(self, "✅ بارگذاری شد", msg)

        except Exception as e:
            CustomMessageBox.critical(self, "❌ خطا", f"خطا در بارگذاری پروژه:\n{str(e)}")

    def closeEvent(self, event):
        self.debate_engine.stop_debate()
        self.prompt_optimizer.cancel_all()
        event.accept()
