import sys
import importlib
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFrame, QMessageBox

class CTWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.custom_window_names = {
            1: "Ominis-OSINT[UNAVAILABLE!]",
            2: "Placeholder Window 2",
            3: "Placeholder Window 3",
            4: "Placeholder Window 4",
            5: "Placeholder Window 5"
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Odinova Digital Tiger:BETA: CT Window Manager [UNAVAILABLE!]")
        self.setGeometry(100, 100, 1000, 685)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        self.setStyleSheet(self.create_stylesheet())

        self.create_navbar(main_layout)
        self.add_separator(main_layout)
        self.create_display_container(main_layout)

    def create_stylesheet(self):
        return """
            QMainWindow {
                background-color: #121212;
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: 2px solid #000000;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 8px;  
            }
            QPushButton:hover {
                background-color: #9E3E3E;
            }
            QPushButton#special_button {
                font-size: 18px;
                padding: 10px 18px;
                background-color: #FF0000;  
                font-weight: bold;         
                border-radius: 8px; 
                border: 3px solid #000000;
            }
            QFrame#separator {
                background-color: #000000;
                height: 2px;
            }
            QFrame#display_container {
                border: 3px solid black;
                background-color: #1E1E1E;
            }
        """

    def create_navbar(self, layout):
        navbar = QWidget()
        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setContentsMargins(0, 0, 0, 0)
        navbar_layout.setSpacing(10)

        for i in range(1, 6):
            button = QPushButton(self.custom_window_names[i])
            button.setObjectName("special_button" if i == 1 else "")
            button.clicked.connect(self.make_button_click_handler(i))
            navbar_layout.addWidget(button)

            if i == 1:
                separator = QFrame()
                separator.setObjectName("separator")
                separator.setFrameShape(QFrame.Shape.VLine)
                separator.setFrameShadow(QFrame.Shadow.Sunken)
                navbar_layout.addWidget(separator)

        layout.addWidget(navbar)

    def make_button_click_handler(self, index):
        def handler():
            self.load_window(index)
        return handler

    def add_separator(self, layout):
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

    def create_display_container(self, layout):
        self.display_container = QFrame()
        self.display_container.setObjectName("display_container")
        self.display_container.setFrameShape(QFrame.Shape.Box)
        self.display_container.setFrameShadow(QFrame.Shadow.Raised)
        self.display_container.setLineWidth(1)

        display_layout = QVBoxLayout(self.display_container)
        display_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        display_layout.addWidget(self.stacked_widget)

        layout.addWidget(self.display_container)

    def load_window(self, index):
        if index == 1:
            QMessageBox.warning(self, "Under Construction", "This window is currently under construction and cannot be loaded.", QMessageBox.StandardButton.Ok)
            return
        
        module_name = f'src.windows.CT.ctwindow_{index}'
        class_name = f'CTWindow{index}'

        try:
            module = importlib.import_module(module_name)
            window_class = getattr(module, class_name)
            window_instance = window_class()
            self.stacked_widget.addWidget(window_instance)
            self.stacked_widget.setCurrentWidget(window_instance)
        except Exception as e:
            print(f"Window loading error: {str(e)}")
            QMessageBox.warning(self, "Error", "An error occurred while loading the window.", QMessageBox.StandardButton.Ok)
