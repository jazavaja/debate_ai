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

QPushButton#settings_btn {
    background-color: #2a3f6e;
    font-size: 13px;
    padding: 10px 18px;
}

QPushButton#settings_btn:hover {
    background-color: #3d5a99;
}

QPushButton#save_btn, QPushButton#load_btn {
    font-size: 12px;
    padding: 8px 14px;
    min-width: 120px;
}

QComboBox {
    background-color: #18203a;
    border: 1px solid #2b3a66;
    border-radius: 10px;
    padding: 8px;
    color: #f2f5fb;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #f2f5fb;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #18203a;
    border: 1px solid #2b3a66;
    color: #f2f5fb;
    selection-background-color: #e94560;
}

QDoubleSpinBox {
    background-color: #18203a;
    border: 1px solid #2b3a66;
    border-radius: 10px;
    padding: 8px;
    color: #f2f5fb;
}

QCheckBox {
    color: #f2f5fb;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #2b3a66;
    border-radius: 4px;
    background-color: #18203a;
}

QCheckBox::indicator:checked {
    background-color: #e94560;
    border-color: #e94560;
}

QTabWidget::pane {
    border: 1px solid #2b3a66;
    border-radius: 10px;
    background-color: #11162e;
}

QTabBar::tab {
    background-color: #1f3162;
    color: #f2f5fb;
    border: 1px solid #2b3a66;
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background-color: #e94560;
    border-color: #e94560;
}

QTabBar::tab:hover {
    background-color: #3d5a99;
}

QTableWidget {
    background-color: #11162e;
    border: 1px solid #2b3a66;
    border-radius: 8px;
    color: #f2f5fb;
    gridline-color: #2b3a66;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #e94560;
}

QHeaderView::section {
    background-color: #1f3162;
    color: #f2f5fb;
    border: 1px solid #2b3a66;
    padding: 6px;
    font-weight: bold;
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
    border: 2px solid #3a4f8a;
    border-radius: 14px;
    margin-top: 16px;
    padding: 18px 14px 14px 14px;
    background-color: #11162e;
    color: #f2f5fb;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 4px 12px;
    color: #e94560;
    background-color: #1a2244;
    border: 1px solid #3a4f8a;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
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