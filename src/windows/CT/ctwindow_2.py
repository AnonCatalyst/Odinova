from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class CTWindow2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("This is CTWindow 2, Which is unavailable.")
        layout.addWidget(label)
