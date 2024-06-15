import sys
import threading
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QTextEdit, QHBoxLayout, QVBoxLayout, QFormLayout, QMenuBar, QMenu, QStatusBar
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from subprocess import call, CalledProcessError
from PyQt6.QtGui import QAction
import subprocess

class Worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    output = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            result = subprocess.run(self.command, capture_output=True, text=True, check=True)
            self.output.emit(result.stdout)
        except subprocess.CalledProcessError as e:
            self.error.emit(f"Error: {e.stderr}")
        except FileNotFoundError:
            # Fix the configuration only once
            if not getattr(self, 'config_fixed', False):
                self.fix_configuration()
                self.config_fixed = True
                # Retry the command after fixing the configuration
                self.run()
            else:
                self.error.emit("Error: blackbird.py not found!")
        finally:
            self.finished.emit()

class SubWindow1(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Blackbird: Username Search")

        # Main layout
        main_layout = QVBoxLayout()

        # Apply dark theme with red touches
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QMenuBar {
                background-color: #2e2e2e;
                color: white;
            }
            QMenuBar::item {
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #ff4444;
            }
            QMenu {
                background-color: #2e2e2e;
                color: white;
            }
            QMenu::item:selected {
                background: #ff4444;
            }
            QLabel, QLineEdit, QTextEdit, QPushButton {
                background-color: #2e2e2e;
                color: white;
            }
            QPushButton {
                border: 2px solid #ff4444;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #ff4444;
            }
            QStatusBar {
                background-color: #2e2e2e;
                color: white;
            }
        """)

        # Label for window title
        self.label = QLabel("Blackbird: Username Search")
        main_layout.addWidget(self.label)

        # Description of Blackbird
        self.description = QLabel(
            "Blackbird is a robust OSINT tool that facilitates rapid searches for user accounts "
            "by username or email across a wide array of platforms, enhancing digital investigations. "
            "Fully integrated with the WhatsMyName project, it supports accurate reverse username searches across 600+ sites."
        )
        self.description.setWordWrap(True)
        main_layout.addWidget(self.description)

        # Form layout for input fields
        form_layout = QFormLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Enter usernames separated by spaces")
        form_layout.addRow("Usernames:", self.username_input)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter emails separated by spaces")
        form_layout.addRow("Emails:", self.email_input)

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.run_by_username_button = QPushButton("Run by Username", self)
        self.run_by_username_button.clicked.connect(self.run_by_username)
        button_layout.addWidget(self.run_by_username_button)

        self.run_by_email_button = QPushButton("Run by Email", self)
        self.run_by_email_button.clicked.connect(self.run_by_email)
        button_layout.addWidget(self.run_by_email_button)

        self.export_to_pdf_button = QPushButton("Export to PDF", self)
        self.export_to_pdf_button.clicked.connect(self.export_to_pdf)
        button_layout.addWidget(self.export_to_pdf_button)

        main_layout.addLayout(button_layout)

        # Output display
        self.output_display = QTextEdit(self)
        self.output_display.setReadOnly(True)
        main_layout.addWidget(self.output_display)

        # Status indicator
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def run_by_username(self):
        usernames = self.username_input.text().strip().split()
        if usernames:
            self.run_blackbird_tool(["--username"] + usernames)

    def run_by_email(self):
        emails = self.email_input.text().strip().split()
        if emails:
            self.run_blackbird_tool(["--email"] + emails)

    def export_to_pdf(self):
        emails = self.email_input.text().strip().split()
        if emails:
            self.run_blackbird_tool(["--email"] + emails + ["--pdf"])

    def run_blackbird_tool(self, args):
        self.output_display.clear()
        command = ["sudo", sys.executable, "src/windows/ottools/Odinova-Blackbird-clone/blackbird.py"] + args

        self.status_label.setText("Running...")

        # Create a worker object and move it to a new thread
        self.worker = Worker(command)
        self.thread = threading.Thread(target=self.worker.run)
        
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.output.connect(self.on_output)

        self.thread.start()

    def on_finished(self):
        self.status_label.setText("Finished")

    def on_error(self, error):
        self.output_display.setPlainText(error)

    def on_output(self, output):
        # Append new output to the existing text
        self.output_display.append(output)
