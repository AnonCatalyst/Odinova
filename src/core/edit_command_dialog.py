from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton

class EditCommandDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Launch Command")

        layout = QVBoxLayout(self)
        self.command_input = QLineEdit(self)
        layout.addWidget(self.command_input)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.accept)
        layout.addWidget(save_button)

    def get_new_command(self):
        return self.command_input.text()
