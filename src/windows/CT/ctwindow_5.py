from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class CTWindow5(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("This is CTWindow 5, which is unavailable.")
        layout.addWidget(label)
