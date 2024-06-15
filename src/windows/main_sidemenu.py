from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QThread, QObject
from PyQt6.QtGui import QPixmap, QColor
import os

class ImageLoader(QObject):
    image_loaded = pyqtSignal(QPixmap)
    finished = pyqtSignal()

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def load_image(self):
        pixmap = QPixmap()
        if pixmap.load(self.file_path):
            self.image_loaded.emit(pixmap)
        self.finished.emit()


class SideMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 0)
        self.layout.setSpacing(10)

        # Add logo image
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.logo_label)

        # Add a border and description label below the logo
        self.logo_separator = QLabel()
        self.logo_separator.setFixedHeight(1)
        self.logo_separator.setStyleSheet("background-color: #888888;")
        self.layout.addWidget(self.logo_separator)

        self.logo_description = QLabel(" ODINOVA MENU ")
        self.logo_description.setStyleSheet("color: #888888; font-size: 10px;")
        self.layout.addWidget(self.logo_description)

        menu_items = ["TOOLBOX", "RESOURCES", "DOCUMENTS", "DOCUMENTER"]
        print(f"Available menu items: {menu_items}")
        for item in menu_items:
            button = QPushButton(item)
            button.setObjectName(item)  # Set object name to identify the button
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: #2E2E2E;
                    color: white;
                    border: none;
                    padding: 10px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3E3E3E;
                }
                """
            )
            button.clicked.connect(self.handle_menu_item_click)  # Connect clicked signal to handler
            self.layout.addWidget(button)

        # Add a border and description label below the buttons
        self.button_separator = QLabel()
        self.button_separator.setFixedHeight(1)
        self.button_separator.setStyleSheet("background-color: #888888;")
        self.layout.addWidget(self.button_separator)

        self.button_description = QLabel(""" ~ Hard2Find DEV-CO 
created Odinova Digital 
Tiger to help make OSINT 
practices more efficient, 
effective, & less tedious. 
Join our discord server 
for support & project 
update notices.""")
        self.button_description.setStyleSheet("color: #888888; font-size: 10px;")
        self.layout.addWidget(self.button_description)

        # Add an additional stretch to move the border label close to the last menu item
        self.layout.addStretch()

        # Load logo image asynchronously
        self.load_logo_image_async()

    def load_logo_image_async(self):
        file_path = os.path.join('src', 'assets', 'icons', 'side_logo.png')
        self.image_loader = ImageLoader(file_path)
        self.image_loader.image_loaded.connect(self.update_logo)
        self.image_loader.finished.connect(self.cleanup_thread)
        self.thread = QThread()
        self.image_loader.moveToThread(self.thread)
        self.thread.started.connect(self.image_loader.load_image)
        self.thread.start()

    def update_logo(self, pixmap):
        self.logo_label.setPixmap(pixmap.scaledToWidth(140))

    def cleanup_thread(self):
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()

    def handle_menu_item_click(self):
        sender = self.sender()  # Get the button that triggered the signal
        if sender:
            item_name = sender.objectName()
            print(f" Menu item clicked: {item_name}")

    def closeEvent(self, event):
        if hasattr(self, 'image_loader'):
            self.cleanup_thread()
        event.accept()