from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class CTWindow4(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("This is CTWindow 4, which is unavailable.")
        layout.addWidget(label)
