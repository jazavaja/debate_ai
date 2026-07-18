# ui/widgets/debate_output.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextBrowser, QPushButton, QProgressBar,
)
from PyQt5.QtCore import Qt
import markdown2

from models.debate_status import DebateStatus, TurnType
from models.debate_turn import DebateTurn


class DebateOutput(QWidget):
    """ویجت نمایش خروجی مناظره."""

    STATUS_LABELS = {
        DebateStatus.PENDING: ("⏳", "در انتظار"),
        DebateStatus.RUNNING: ("🔄", "در حال تولید"),
        DebateStatus.COMPLETED: ("✅", "تکمیل شده"),
        DebateStatus.FAILED: ("❌", "متوقف شده (خطا)"),
        DebateStatus.STOPPED: ("⏹️", "متوقف شده"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panel_frame")
        self._setup_ui()
        self._turns: list[DebateTurn] = []
        self._stream_buffers: dict[int, str] = {}
        self._current_status = DebateStatus.PENDING

    def _setup_ui(self):
        layout = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel("📄 خروجی مناظره:"))
        header.addStretch()

        self.status_label = QLabel("⏳ در انتظار")
        self.status_label.setStyleSheet("color: #888; font-size: 13px;")
        header.addWidget(self.status_label)

        self.save_btn = QPushButton("💾 ذخیره فایل")
        self.save_btn.setEnabled(False)
        header.addWidget(self.save_btn)

        self.clear_btn = QPushButton("🗑️ پاک کردن")
        header.addWidget(self.clear_btn)

        layout.addLayout(header)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.output_text = QTextBrowser()
        self.output_text.setObjectName("output_area")
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText(
            "خروجی مناظره اینجا نمایش داده می‌شود...\n"
            "پس از اتمام، دکمه ذخیره را بزنید."
        )
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def _turn_header(self, turn: DebateTurn) -> str:
        if turn.turn_type == TurnType.MODERATOR_INTRO:
            return f"<hr><h2>🎙️ معرفی مجری | {turn.speaker}</h2>"
        if turn.turn_type == TurnType.MODERATOR_INTERVENTION:
            return f"<hr><h3>🎙️ مداخله مجری | {turn.speaker}</h3>"
        return f"<hr><h3>نوبت {turn.turn_number} | {turn.speaker}</h3>"

    def add_turn(self, turn: DebateTurn):
        self._turns.append(turn)
        html = markdown2.markdown(turn.content)
        self.output_text.append(self._turn_header(turn) + html)
        self._scroll_bottom()
        self.save_btn.setEnabled(True)

    def start_turn_stream(self, turn_number: int, speaker: str, turn_type: str = "debater"):
        if turn_type == TurnType.MODERATOR_INTRO.value:
            header = f"<hr><h2>🎙️ معرفی مجری | {speaker}</h2>"
        elif turn_type == TurnType.MODERATOR_INTERVENTION.value:
            header = f"<hr><h3>🎙️ مداخله مجری | {speaker}</h3>"
        else:
            header = f"<hr><h3>نوبت {turn_number} | {speaker}</h3>"
        self.output_text.append(header)
        self._scroll_bottom()

    def append_turn_chunk(self, turn_number: int, chunk: str):
        if not chunk:
            return
        if turn_number not in self._stream_buffers:
            self._stream_buffers[turn_number] = ""
        self._stream_buffers[turn_number] += chunk
        self.output_text.insertPlainText(chunk)
        self._scroll_bottom()

    def append_conclusion_chunk(self, chunk: str):
        if not chunk:
            return
        if not hasattr(self, "_conclusion_started") or not self._conclusion_started:
            self.output_text.append("<hr><h2>📋 نتیجه‌گیری مجری</h2>")
            self._conclusion_started = True
        self.output_text.insertPlainText(chunk)
        self._scroll_bottom()

    def finalize_streamed_turn(self, turn: DebateTurn):
        self._stream_buffers.pop(turn.turn_number, None)
        if not any(t.turn_number == turn.turn_number for t in self._turns):
            self._turns.append(turn)
        self._render_all_turns()
        self.save_btn.setEnabled(True)

    def _render_all_turns(self):
        self.output_text.clear()
        for turn in self._turns:
            html = markdown2.markdown(turn.content)
            self.output_text.append(self._turn_header(turn) + html)
        self._scroll_bottom()

    def set_conclusion(self, conclusion: str):
        header = "<hr><h2>📋 نتیجه‌گیری مجری</h2>"
        html = markdown2.markdown(conclusion)
        self.output_text.append(header + html)
        self.save_btn.setEnabled(True)
        self.progress.setVisible(False)
        self._conclusion_started = False
        self._scroll_bottom()

    def set_status(self, status: DebateStatus, error_message: str = ""):
        self._current_status = status
        icon, label = self.STATUS_LABELS.get(status, ("❓", status.value))
        text = f"{icon} {label}"
        if error_message and status == DebateStatus.FAILED:
            text += f" — {error_message[:80]}"
        self.status_label.setText(text)

        colors = {
            DebateStatus.RUNNING: "#4fc3f7",
            DebateStatus.COMPLETED: "#66bb6a",
            DebateStatus.FAILED: "#ef5350",
            DebateStatus.STOPPED: "#ffa726",
        }
        color = colors.get(status, "#888")
        self.status_label.setStyleSheet(f"color: {color}; font-size: 13px;")

    def set_progress(self, current: int, total: int):
        self.progress.setVisible(True)
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.progress.setFormat(f"در حال تولید... {current}/{total}")

    def reset(self):
        self._turns.clear()
        self._stream_buffers.clear()
        self._conclusion_started = False
        self.output_text.clear()
        self.save_btn.setEnabled(False)
        self.progress.setVisible(False)
        self.set_status(DebateStatus.PENDING)

    def get_turns(self) -> list[DebateTurn]:
        return self._turns.copy()

    def _scroll_bottom(self):
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
