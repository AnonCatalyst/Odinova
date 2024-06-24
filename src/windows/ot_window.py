from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QScrollArea, QSizePolicy, QToolBar
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize
from subprocess import call, CalledProcessError
from src.windows.sub_window1 import SubWindow1
from src.windows.sub_window2 import SubWindow2
from src.windows.pydork_window import PyDorkWindow
from src.windows.getrails_window import GetRailsWindow
from src.windows.underworldquest_window import UnderworldQuestWindow  # Import UnderworldQuest

class OTWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Odinova Digital Tiger:  'TOOLBOX | Other Tools'")
        self.setGeometry(100, 100, 800, 650)
        self.setWindowIcon(QIcon("src/assets/icons/main_icon.png"))
        
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.toolbar.setIconSize(QSize(24, 24))  # Set icon size for the toolbar

        self.sub_windows = {
            "Blackbird": SubWindow1(), 
            "Holehe": SubWindow2(), 
            "PyDork": PyDorkWindow(),
            "UnderworldQuest": UnderworldQuestWindow(),  # Include UnderworldQuestWindow
            "GetRails": GetRailsWindow()  # Include GetRailsWindow
        }
        self.current_window = None
        self.setup_toolbar()
        
        self.status_label = QLabel("", self.statusBar())
        self.statusBar().addPermanentWidget(self.status_label)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        scroll_area = QScrollArea()
        layout.addWidget(scroll_area)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        scroll_layout = QVBoxLayout(scroll_content)
        
        self.add_welcome_message(scroll_layout)
        
        install_button = QPushButton("Install Tools")
        install_button.setIcon(QIcon("src/assets/icons/install.png"))
        install_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #000000;
                padding: 5px;
                background-color: #1e1e1e;
                color: white;
            }
            QPushButton:hover { background-color: #2e2e2e; }
            QPushButton:pressed { background-color: #3e3e3e; }
            QPushButton:focus { outline: none; }
        """)
        install_button.clicked.connect(self.install_tools)
        layout.addWidget(install_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add sub-windows initially
        for window in self.sub_windows.values():
            window.hide()
            scroll_layout.addWidget(window)

    def setup_toolbar(self):
        for title in self.sub_windows:
            action = QAction(title, self)
            action.triggered.connect(lambda checked, title=title: self.switch_window(title))
            self.toolbar.addAction(action)

    def switch_window(self, window_title):
        new_window = self.sub_windows.get(window_title)
        if new_window:
            if self.current_window:
                self.current_window.hide()
            new_window.show()
            self.current_window = new_window
            self.status_label.setText(f"Changed to {new_window.windowTitle()}")

    def add_welcome_message(self, layout):
        welcome_text = (
            "<h2>Welcome to the OT Window!</h2>"
            "<p>We are thrilled to have you here. This interface integrates powerful OSINT tools ready for you to use.</p>"
            "<p><b>To get started:</b></p>"
            "<ul>"
            "<li>Click the <b>Install Tools</b> button to install the necessary tools.</li>"
            "<li>Use the buttons on the toolbar to navigate between different tools available in the GUI.</li>"
            "</ul>"
            "<p>We hope you find this tool useful for your OSINT needs!</p>"
        )
        self.add_description(layout, welcome_text)

    def add_description(self, layout, text):
        description_label = QLabel()
        description_label.setText(text)
        description_label.setOpenExternalLinks(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        description_label.setStyleSheet("""
            QLabel {
                border-bottom: 2px solid #ff4444;
                padding: 10px;
                background-color: #2e2e2e;
                color: white;
            }
        """)
        layout.addWidget(description_label)

    def install_tools(self):
        try:
            call(["sudo", "bash", "install_tools.sh"])
            self.status_label.setText("Tools installed successfully.")
        except FileNotFoundError:
            self.status_label.setText("Error: install_tools.sh not found!")
        except CalledProcessError as e:
            self.status_label.setText(f"Installation failed: {e}")
