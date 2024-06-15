from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

class DesignHandler:
    current_theme = "dark"  # Default to dark theme

    @staticmethod
    def toggle_theme():
        if DesignHandler.current_theme == "dark":
            DesignHandler.current_theme = "light"
        else:
            DesignHandler.current_theme = "dark"

    @staticmethod
    def apply_theme(widget):
        if DesignHandler.current_theme == "dark":
            DesignHandler.apply_dark_theme(widget)
        else:
            DesignHandler.apply_light_theme(widget)

    @staticmethod
    def apply_dark_theme(widget):
        widget.setStyleSheet("""
            background-color: #1E1E1E;
            color: white;
        """)

    @staticmethod
    def apply_light_theme(widget):
        widget.setStyleSheet("""
            background-color: white;
            color: black;
        """)

    @staticmethod
    def apply_default_background_color(widget):
        widget.setStyleSheet("""
            background-color: #000000;
            color: white;
        """)

    @staticmethod
    def apply_background_color(widget, color):
        widget.setStyleSheet(f"""
            background-color: {color};
            color: white;
        """)

    @staticmethod
    def create_label(text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        DesignHandler.apply_theme(label)
        return label

    @staticmethod
    def create_button(text):
        button = QPushButton(text)
        button.setStyleSheet("""
            background-color: #3E3E3E;
            border: none;
            padding: 10px;
            font-size: 16px;
        """)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    @staticmethod
    def create_vertical_layout():
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        return layout

    @staticmethod
    def create_central_widget():
        central_widget = QWidget()
        DesignHandler.apply_theme(central_widget)  # Default to dark mode
        return central_widget

    @staticmethod
    def apply_background_image(widget, image_path):
        widget.setStyleSheet(f"""
            background-image: url({image_path});
            background-repeat: no-repeat;
            background-position: center;
            background-size: full;
        """)

    @staticmethod
    def reset_border(widget):
        widget.setStyleSheet("border: 2px solid #FFFFFF;")  # Set to default border style
