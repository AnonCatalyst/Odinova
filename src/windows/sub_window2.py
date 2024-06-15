import subprocess
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QMessageBox, QApplication, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread

class HoleheWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    output_ready = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, email, create_csv, only_used):
        super().__init__()
        self.email = email
        self.create_csv = create_csv
        self.only_used = only_used

    def run(self):
        try:
            command = ["holehe", self.email]
            if self.create_csv:
                command.append("--csv")
            if self.only_used:
                command.append("--only-used")
            output = subprocess.run(command, check=True, capture_output=True, text=True).stdout
            self.output_ready.emit(output)
            self.status_update.emit("Holehe tool finished.")
        except subprocess.CalledProcessError as e:
            self.error.emit(f"Error: {e}")
            self.status_update.emit(f"Error: {e}")
        finally:
            self.finished.emit()

class SubWindow2(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Holehe: Email Registry Search")
        self.setGeometry(100, 100, 800, 600)  # Larger window size
        self.init_ui()
        self.worker_thread = None  # Keep a reference to the worker thread

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setStyleSheet(
            """
            background-color: #1f1f1f;
            color: #ffffff;
            border: 2px solid #000000;
            """
        )

        # Label for window title
        self.label = QLabel("Holehe: Email Registry Search")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            """
            font-size: 24px;
            padding: 20px;
            """
        )
        main_layout.addWidget(self.label)

        # Description of Holehe
        self.description_label = QLabel(
            """
Holehe checks if an email is attached to an account on various websites, such as Twitter, Instagram, Imgur, and more than 120 others. It retrieves information using the forgotten password function without alerting the target email.
            """
        )
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(
            """
            padding: 10px;
            """
        )
        main_layout.addWidget(self.description_label)

        # Input field for email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")
        self.email_input.setStyleSheet(
            """
            padding: 10px;
            background-color: #333333;
            color: #ffffff;
            border: 2px solid #000000;
            """
        )
        main_layout.addWidget(self.email_input)

        # Checkbox for "Create CSV" option
        self.create_csv_checkbox = QCheckBox("Create CSV")
        self.create_csv_checkbox.setStyleSheet(
            """
            color: #ffffff;
            """
        )
        main_layout.addWidget(self.create_csv_checkbox)

        # Checkbox for "Only Used" option
        self.only_used_checkbox = QCheckBox("Only Used")
        self.only_used_checkbox.setStyleSheet(
            """
            color: #ffffff;
            """
        )
        main_layout.addWidget(self.only_used_checkbox)

        # Button to run Holehe tool
        self.run_button = QPushButton("Run Holehe Tool")
        self.run_button.setStyleSheet(
            """
            padding: 10px;
            background-color: #007bff;
            color: #ffffff;
            border: 2px solid #000000;
            """
        )
        self.run_button.clicked.connect(self.run_holehe_tool)
        main_layout.addWidget(self.run_button)

        # TextEdit to display output
        self.output_textedit = QTextEdit()
        self.output_textedit.setStyleSheet(
            """
            padding: 10px;
            background-color: #333333;
            color: #ffffff;
            border: 2px solid #000000;
            """
        )
        main_layout.addWidget(self.output_textedit)

        # Label to display status updates
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            """
            padding: 10px;
            """
        )
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        self.worker = None  # Initialize worker instance

    def run_holehe_tool(self):
        email = self.email_input.text().strip()
        create_csv = self.create_csv_checkbox.isChecked()
        only_used = self.only_used_checkbox.isChecked()
        if email:
            self.worker = HoleheWorker(email, create_csv, only_used)
            self.worker.finished.connect(self.process_finished)
            self.worker.error.connect(self.process_error)
            self.worker.output_ready.connect(self.display_output)
            self.worker.status_update.connect(self.update_status)

            # Create a new QThread instance for each run
            self.worker_thread = QThread()
            self.worker.moveToThread(self.worker_thread)
            self.worker_thread.started.connect(self.worker.run)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)  # Clean up the thread
            self.worker_thread.start()
            self.status_label.setText("Running Holehe tool...")
            # Disable UI elements during execution
            self.run_button.setEnabled(False)
            self.email_input.setEnabled(False)
            self.create_csv_checkbox.setEnabled(False)
            self.only_used_checkbox.setEnabled(False)
        else:
            QMessageBox.warning(self, "Holehe Tool", "Please enter an email address.")

    def display_output(self, output):
        self.output_textedit.setText(output)

    def update_status(self, status):
        self.status_label.setText(status)

    def process_finished(self):
        # Re-enable UI elements
        self.run_button.setEnabled(True)
        self.email_input.setEnabled(True)
        self.create_csv_checkbox.setEnabled(True)
        self.only_used_checkbox.setEnabled(True)

    def process_error(self, error_message):
        # Re-enable UI elements
        self.process_finished()
        QMessageBox.critical(self, "Error", error_message)
