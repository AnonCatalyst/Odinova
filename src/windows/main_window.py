import os
import json
import sys
import time
import threading
from PyQt6.QtWidgets import QApplication, QGroupBox, QGridLayout
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QPushButton, QToolBar, QWidget, QFrame, QVBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import QTimer, QRect, QPropertyAnimation, Qt, QObject, pyqtSignal, QEasingCurve, QRectF
from src.core.design_handler import DesignHandler
from src.core.settings import Settings
from src.windows.main_sidemenu import SideMenu
from src.core.input_handler import InputHandler
from src.windows.settings_window import SettingsWindow
from src.windows.docs_window import DocumentsWindow
from src.windows.documenter import Documenter 
from src.core.design_handler import DesignHandler
from src.windows.resources_window import ResourcesWindow
from src.windows.toolbox_window import ToolBoxWindow
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QImage, QPen, QPalette


class ImageLoader(QObject):
    finished = pyqtSignal()

    def __init__(self, image_folder, config_file):
        super().__init__()
        self.image_folder = image_folder
        self.config_file = config_file
        self.images = []

    def load_images(self):
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                config = json.load(f)
                for image_file in config:
                    image_path = os.path.join(self.image_folder, image_file)
                    if os.path.exists(image_path):
                        pixmap = QPixmap(image_path)
                        self.images.append(pixmap)
        self.finished.emit()

class SlideshowWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.image_folder = "src/assets/backgrounds"
        self.config_file = "src/configs/bg-config.json"

        self.current_image_index = 0
        self.next_image_index = 1

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center-align the image
        self.label.setStyleSheet(
            "border: 4px solid black; background-color: #101010;"
        )  # Set border and background color
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.setContentsMargins(20, 20, 20, 20)  # Add some margin around the label
        self.setLayout(self.layout)


        self.loading_label = QLabel("Loading images...")
        self.loading_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center-align the loading message

        self.layout.addWidget(self.loading_label)

        self.loading_label.raise_()  # Raise loading label above the image label

        self.timer = QTimer()
        self.timer.timeout.connect(self.show_next_image)

        self.image_loader = ImageLoader(self.image_folder, self.config_file)
        self.image_loader.finished.connect(self.start_slideshow)

        self.load_images_thread = threading.Thread(
            target = self.image_loader.load_images
        )
        self.load_images_thread.start()
        # Set fixed window size
        self.setFixedSize(945, 550)


    def show_next_image(self):
        pixmap_current = self.image_loader.images[self.current_image_index]
        pixmap_next = self.image_loader.images[self.next_image_index]

        label_size = self.label.size()
        pixmap_current = pixmap_current.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        pixmap_next = pixmap_next.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Create a new pixmap for the crossfade
        crossfade_pixmap = QPixmap(label_size)
        crossfade_pixmap.fill(Qt.GlobalColor.transparent)

        # Create a QPainter to draw the current and next images onto the crossfade pixmap
        painter = QPainter(crossfade_pixmap)
        painter.drawPixmap(0, 0, pixmap_current)
        painter.drawPixmap(0, 0, pixmap_next)

        # Check if the timer is active before accessing its properties
        if self.timer.isActive():
            opacity = 1.0 - self.timer.remainingTime() / self.timer.interval()
        else:
            opacity = 1.0  # Set default opacity when timer is not active
        painter.setOpacity(opacity)
        painter.drawPixmap(0, 0, pixmap_next)

        painter.end()

        self.label.setPixmap(crossfade_pixmap)

        # Update indices for next iteration
        self.current_image_index = (self.current_image_index + 1) % len(
            self.image_loader.images
        )
        self.next_image_index = (self.current_image_index + 1) % len(
            self.image_loader.images
        )
    def start_slideshow(self):
        self.loading_label.hide() # Loading ... set off for now 

        if self.image_loader.images:           
            self.timer.start(4500)  # Start the slideshow timer after images are loaded
        else:
            self.label.setText("Background images not found.")


class ContactsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        slideshow_widget = SlideshowWidget()
        slideshow_widget.show()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = DesignHandler.create_label("📇 Contact Information")
        title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            margin-bottom: 30px; 
            background-image: url('src/assets/backgrounds/contacts.png'); 
            background-size: cover;  /* Ensure the image covers the entire label */
            background-position: center;  /* Center the image */
        """)
        layout.addWidget(title_label)

        # Personal Contacts Group
        personal_group_box = QGroupBox("Developer Contacts")
        personal_group_layout = QGridLayout()
        personal_group_box.setLayout(personal_group_layout)

        github_label = DesignHandler.create_label("GitHub: <a href='https://github.com/AnonCatalyst'>AnonCatalyst</a>")
        github_label.setOpenExternalLinks(True)
        personal_group_layout.addWidget(github_label, 0, 0)

        discord_label = DesignHandler.create_label("Discord: <a href='https://discord.gg/GkKP3XNwak'>Support Server</a>")
        discord_label.setOpenExternalLinks(True)
        personal_group_layout.addWidget(discord_label, 1, 0)

        instagram_label = DesignHandler.create_label("Instagram: <a href='https://instagram.com/istoleyourbutter'>istoleyourbutter</a>")
        instagram_label.setOpenExternalLinks(True)
        personal_group_layout.addWidget(instagram_label, 2, 0)

        email_label = DesignHandler.create_label("Email: <a href='mailto:hard2find.co.01@gmail.com'>hard2find.co.01@gmail.com</a>")
        email_label.setOpenExternalLinks(True)
        personal_group_layout.addWidget(email_label, 3, 0)

        layout.addWidget(personal_group_box)

        # Separator Line
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.Shape.HLine)
        separator_line.setStyleSheet("color: #888888; margin: 20px 0;")
        layout.addWidget(separator_line)

        # Company Contacts Group
        company_group_box = QGroupBox("Company")
        company_group_layout = QGridLayout()
        company_group_box.setLayout(company_group_layout)

        company_name_label = DesignHandler.create_label(" Hard2Find DEV-CO - (development company) ")
        company_group_layout.addWidget(company_name_label, 0, 0)

        layout.addWidget(company_group_box)

        self.setLayout(layout)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ODINOVA - Digital Tiger:  'BETA'")
        self.setGeometry(100, 100, 1080, 600)

        self.side_menu_closed = False
        self.side_menu_width = 120
        self.animation_duration = 900  
        self.animation = QPropertyAnimation()

        self.initUI()

        # Apply dark theme
        DesignHandler.apply_dark_theme(self)

    def initUI(self):
        self.central_widget = DesignHandler.create_central_widget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Initialize side menu
        self.side_menu = SideMenu(self)
        self.side_menu.setMaximumWidth(self.side_menu_width)
        self.main_layout.addWidget(self.side_menu)

        # Connect side menu buttons to their respective functions
        for button in self.side_menu.findChildren(QPushButton):
            if button.objectName() == "DOCUMENTS":
                button.clicked.connect(self.open_documents)
            elif button.objectName() == "DOCUMENTER":
                button.clicked.connect(self.open_documenter)
            elif button.objectName() == "RESOURCES":
                button.clicked.connect(self.open_resources)
            elif button.objectName() == "TOOLBOX":
                button.clicked.connect(self.open_toolbox)


        # Separator line
        self.separator_line = QFrame()
        self.separator_line.setFrameShape(QFrame.Shape.VLine)
        self.separator_line.setStyleSheet("color: #888888;")
        self.main_layout.addWidget(self.separator_line)

        # Content widget
        self.content_widget = QWidget()
        self.main_layout.addWidget(self.content_widget)

        self.HOME_layout = QVBoxLayout(self.content_widget)
        self.HOME_layout.setContentsMargins(0, 0, 0, 0)
        self.HOME_layout.setSpacing(0)

        # Toolbar
        self.setup_toolbar()
        self.slideshow_widget = SlideshowWidget()
        self.HOME_layout.addWidget(self.slideshow_widget)

    def setup_toolbar(self):
        settings_toolbar = QToolBar()
        settings_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, settings_toolbar)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        settings_toolbar.addWidget(self.settings_button)

        self.home_button = QPushButton("Home")
        self.home_button.clicked.connect(self.go_to_home)
        settings_toolbar.addWidget(self.home_button)

        self.contacts_button = QPushButton("Contacts")
        self.contacts_button.clicked.connect(self.open_contacts)
        settings_toolbar.addWidget(self.contacts_button)

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

    def go_to_home(self):
        self.clear_HOME_layout()

        self.slideshow_widget = SlideshowWidget()
        self.HOME_layout.addWidget(self.slideshow_widget)

    def open_contacts(self):
        self.clear_HOME_layout()
        contacts_widget = ContactsWidget()
        self.HOME_layout.addWidget(contacts_widget)

    def open_documents(self):
        self.clear_HOME_layout()
        documents_widget = DocumentsWindow()
        documents_widget.open_document.connect(self.open_document_in_documenter)
        self.HOME_layout.addWidget(documents_widget)

    def open_document_in_documenter(self, file_path):
        self.clear_HOME_layout()
        documenter_widget = Documenter()
        documenter_widget.load_file(file_path)
        self.HOME_layout.addWidget(documenter_widget)

    def clear_HOME_layout(self):
        while self.HOME_layout.count():
            child = self.HOME_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def open_documenter(self):
        self.clear_HOME_layout()
        documenter_widget = Documenter()
        self.HOME_layout.addWidget(documenter_widget)

    def open_toolbox(self):
        # Set up ToolBoxWindow
        self.clear_HOME_layout()
        tool_box_window = ToolBoxWindow()
        self.HOME_layout.addWidget(tool_box_window)

    def open_resources(self):
        self.clear_HOME_layout()
        resources_widget = ResourcesWindow()
        self.HOME_layout.addWidget(resources_widget)

    def handle_button_click(self):
        pass  # Apply changes to my MainWindow

