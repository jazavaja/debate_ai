# ui/styles.py
"""
استایل‌های QSS برای UI مدرن و تیره
"""

DARK_THEME = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget {
    font-family: 'Segoe UI', 'Tahoma', sans-serif;
    font-size: 13px;
    color: #eaeaea;
}

QLabel {
    color: #eaeaea;
    font-weight: bold;
}

QLineEdit, QTextEdit, QSpinBox {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 8px;
    color: #eaeaea;
    selection-background-color: #e94560;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #e94560;
}

QPushButton {
    background-color: #0f3460;
    color: #eaeaea;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
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
    background-color: #2a2a4a;
    color: #666;
}

QPushButton#optimize_btn {
    background-color: #533483;
    font-size: 11px;
    padding: 6px 12px;
    min-width: 80px;
}

QPushButton#optimize_btn:hover {
    background-color: #7b2cbf;
}

QPushButton#start_btn {
    background-color: #e94560;
    font-size: 14px;
    padding: 12px 30px;
}

QPushButton#start_btn:hover {
    background-color: #ff6b6b;
}

QPushButton#stop_btn {
    background-color: #c0392b;
}

QProgressBar {
    border: 2px solid #0f3460;
    border-radius: 5px;
    text-align: center;
    color: #eaeaea;
}

QProgressBar::chunk {
    background-color: #e94560;
    border-radius: 3px;
}

QGroupBox {
    border: 2px solid #0f3460;
    border-radius: 10px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #e94560;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QScrollArea {
    border: none;
}

QTextEdit#output_area {
    background-color: #0f0f23;
    font-family: 'Consolas', monospace;
    font-size: 12px;
    line-height: 1.6;
}
"""