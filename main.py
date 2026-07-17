# main.py
import sys
import traceback
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        window = MainWindow()
        window.show()

        sys.exit(app.exec_())
    except Exception as e:
        print(f"خطا: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()