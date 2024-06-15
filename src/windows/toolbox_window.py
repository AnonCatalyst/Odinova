from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap

# The CTWindow and OTWindow classes
from src.windows.ct_window import CTWindow
from src.windows.ot_window import OTWindow

class ToolBoxWindow(QWidget):
    customToolsRequested = pyqtSignal()
    otherToolsRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.ct_window = None  # Placeholder for the custom tools window instance
        self.ot_window = None  # Placeholder for the other tools window instance

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Banner Image
        self.banner_label = QLabel(self)
        self.set_banner_image()
        self.banner_label.setFixedHeight(130)
        self.banner_label.setFixedWidth(900)
        self.banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.banner_label)

        # Add a border and description label below 
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setStyleSheet("color: #404040;")
        main_layout.addWidget(self.separator)

        # Horizontal layout for the buttons and descriptions
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Custom Tools Section
        custom_tools_layout = QVBoxLayout()
        custom_tools_button = QPushButton("Custom Tools")
        custom_tools_button.setStyleSheet(
            """
            QPushButton {
                background-color: #306020;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #508010;
            }
            """
        )
        custom_tools_button.clicked.connect(self.open_ct_window)

        custom_tools_desc = QLabel(
            "Discover tools created by Hard2Find DEV-CO & AnonCatalyst."
        )
        custom_tools_desc.setStyleSheet("color: #666666; font-size: 12px;")
        custom_tools_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        custom_tools_layout.addWidget(custom_tools_button)
        custom_tools_layout.addWidget(custom_tools_desc)
        buttons_layout.addLayout(custom_tools_layout)

        # Divider Line
        divider_line = QFrame()
        divider_line.setFrameShape(QFrame.Shape.VLine)
        divider_line.setStyleSheet("color: #303030;")
        buttons_layout.addWidget(divider_line)

        # Other Tools Section
        other_tools_layout = QVBoxLayout()
        other_tools_button = QPushButton("Other Tools")
        other_tools_button.setStyleSheet(
            """
            QPushButton {
                background-color: #105050;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #006080;
            }
            """
        )
        other_tools_button.clicked.connect(self.open_ot_window)

        other_tools_desc = QLabel(
            "Discover tools developed by others."
        )
        other_tools_desc.setStyleSheet("color: #666666; font-size: 12px;")
        other_tools_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        other_tools_layout.addWidget(other_tools_button)
        other_tools_layout.addWidget(other_tools_desc)
        buttons_layout.addLayout(other_tools_layout)

        main_layout.addLayout(buttons_layout)

        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setStyleSheet("color: #404040;")
        main_layout.addWidget(self.separator)

    def set_banner_image(self):
        pixmap = QPixmap('src/assets/backgrounds/default.png')
        self.banner_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        self.set_banner_image()

    def open_ct_window(self):
        if not self.ct_window:
            self.ct_window = CTWindow()
        self.ct_window.show()
        self.ct_window.raise_()
        self.ct_window.activateWindow()

    def open_ot_window(self):
        if not self.ot_window:
            self.ot_window = OTWindow()
        self.ot_window.show()
        self.ot_window.raise_()
        self.ot_window.activateWindow()
