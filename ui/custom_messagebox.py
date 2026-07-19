# ui/custom_messagebox.py
"""
CustomMessageBox - QMessageBox با استایل تیره/روشن
"""

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QFont


class CustomMessageBox(QMessageBox):
    """کلاس سفارشی برای QMessageBox با زمینه سیاه و متن سفید"""

    DARK_STYLE = """
    QMessageBox {
        background-color: #0f1024;
    }
    QMessageBox QLabel {
        color: #f2f5fb;
    }
    QMessageBox QPushButton {
        background-color: #1f3162;
        color: #f2f5fb;
        border: 1px solid transparent;
        border-radius: 6px;
        padding: 6px 18px;
        font-weight: bold;
        min-width: 60px;
    }
    QMessageBox QPushButton:hover {
        background-color: #e94560;
    }
    QMessageBox QPushButton:pressed {
        background-color: #c73e54;
    }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self.DARK_STYLE)
        self.setFont(QFont('Segoe UI', 11))

    @staticmethod
    def information(parent, title: str, text: str):
        """نمایش پیام اطلاعاتی"""
        msg = CustomMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    @staticmethod
    def warning(parent, title: str, text: str):
        """نمایش پیام هشدار"""
        msg = CustomMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()

    @staticmethod
    def critical(parent, title: str, text: str):
        """نمایش پیام خطا"""
        msg = CustomMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    @staticmethod
    def question(parent, title: str, text: str):
        """نمایش پیام سؤال و برگرداندن جواب"""
        msg = CustomMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec_()
        return result == QMessageBox.Yes
