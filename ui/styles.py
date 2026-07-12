# ui/styles.py
"""
استایل‌های QSS برای UI مدرن و تیره
"""

DARK_THEME = """
QMainWindow {
    background-color: #101123;
}

QWidget {
    font-family: 'Segoe UI', 'Tahoma', sans-serif;
    font-size: 13px;
    color: #f2f5fb;
}

QLabel {
    color: #f7f7f7;
    font-weight: 600;
}

QLabel#section_title {
    color: #e94560;
    font-size: 18px;
    font-weight: bold;
}

QLineEdit, QTextEdit, QSpinBox {
    background-color: #18203a;
    border: 1px solid #2b3a66;
    border-radius: 10px;
    padding: 10px;
    color: #f2f5fb;
    selection-background-color: #e94560;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #e94560;
}

QPushButton {
    background-color: #1f3162;
    color: #f2f5fb;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: bold;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #e94560;
}

QPushButton:pressed {
    background-color: #c73e54;
}

QPushButton:disabled {
    background-color: #2a2f4f;
    color: #7f8fa4;
}

QPushButton#optimize_btn {
    background-color: #3d2a69;
    font-size: 11px;
    padding: 8px 14px;
    min-width: 96px;
}

QPushButton#optimize_btn:hover {
    background-color: #6b45c7;
}

QPushButton#start_btn {
    background-color: #e94560;
    font-size: 14px;
    padding: 12px 26px;
}

QPushButton#start_btn:hover {
    background-color: #ff6b6b;
}

QPushButton#stop_btn {
    background-color: #c0392b;
}

QProgressBar {
    border: 1px solid #2b3a66;
    border-radius: 8px;
    text-align: center;
    color: #f2f5fb;
    background-color: #111629;
}

QProgressBar::chunk {
    background-color: #e94560;
    border-radius: 8px;
}

QGroupBox {
    border: 1px solid #2b3a66;
    border-radius: 14px;
    margin-top: 12px;
    padding: 16px;
    background-color: #11162e;
    color: #f2f5fb;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
}

QScrollArea {
    border: none;
    background-color: #101123;
}

QScrollArea QWidget {
    background-color: #101123;
}

QGroupBox QLabel, QLabel {
    color: #f2f5fb;
}

QLineEdit, QTextEdit, QSpinBox {
    background-color: #11162e;
    border: 1px solid #2b3a66;
    border-radius: 10px;
    padding: 10px;
    color: #f2f5fb;
}

QTextEdit {
    background-color: #101429;
    selection-background-color: #e94560;
}

QPushButton {
    min-height: 36px;
}

QFrame#panel_frame {
    background-color: #0f1024;
    border: 1px solid #2b3a66;
    border-radius: 16px;
}

QTextEdit#output_area {
    background-color: #0c0f1f;
    color: #f5f7ff;
    font-family: 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.6;
    border: 1px solid #273659;
    border-radius: 10px;
}
"""