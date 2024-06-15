# src/app.py

import sys
from PyQt6.QtWidgets import QApplication
from src.windows.main_window import MainWindow
from PyQt6.QtGui import QIcon

class App:
    @staticmethod
    def run():
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon('src/assets/icons/main_icon.png'))

        main_window = MainWindow()
        main_window.show()

        sys.exit(app.exec())

if __name__ == "__main__":
    App.run()

