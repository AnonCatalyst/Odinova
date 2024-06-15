from PyQt6.QtWidgets import QLineEdit

class InputHandler:
    @staticmethod
    def create_line_edit(background_color="#333333"):
        line_edit = QLineEdit()
        line_edit.setStyleSheet(f"background-color: {background_color}; color: white;")
        return line_edit

