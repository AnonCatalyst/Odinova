import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QComboBox, QDateEdit, QApplication, QCheckBox, QGroupBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QProcess

class CTWindow1(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Query input
        self.query_label = QLabel("Query:")
        self.query_input = QLineEdit()
        self.layout.addWidget(self.query_label)
        self.layout.addWidget(self.query_input)

        # Optional Inputs Group
        self.optional_group = QGroupBox("Optional Inputs")
        self.optional_layout = QHBoxLayout()  # Horizontal layout
        self.optional_group.setLayout(self.optional_layout)

        # Language
        self.language_checkbox = QCheckBox("Language:")
        self.language_input = QComboBox()
        self.language_input.addItems(["en", "es", "fr", "de"])
        self.optional_layout.addWidget(self.language_checkbox)
        self.optional_layout.addWidget(self.language_input)

        # Country
        self.country_checkbox = QCheckBox("Country:")
        self.country_input = QComboBox()
        self.country_input.addItems(["US", "FR", "DE", "ES"])
        self.optional_layout.addWidget(self.country_checkbox)
        self.optional_layout.addWidget(self.country_input)

        # Start Date
        self.start_date_checkbox = QCheckBox("Start Date:")
        self.start_date_input = QDateEdit()
        self.start_date_input.setDisplayFormat('MM/dd/yyyy')
        self.start_date_input.setDate(QDate.currentDate())
        self.optional_layout.addWidget(self.start_date_checkbox)
        self.optional_layout.addWidget(self.start_date_input)

        # End Date
        self.end_date_checkbox = QCheckBox("End Date:")
        self.end_date_input = QDateEdit()
        self.end_date_input.setDisplayFormat('MM/dd/yyyy')
        self.end_date_input.setDate(QDate.currentDate())
        self.optional_layout.addWidget(self.end_date_checkbox)
        self.optional_layout.addWidget(self.end_date_input)

        self.layout.addWidget(self.optional_group)

        # Run Script button
        self.run_button = QPushButton("Run Ominis-OSINT")
        self.run_button.clicked.connect(self.run_script)
        self.layout.addWidget(self.run_button)

        # Output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)

        # Status label
        self.status_label = QLabel("Status: Ready")
        self.layout.addWidget(self.status_label)

        # Set layout and window title
        self.setLayout(self.layout)
        self.setWindowTitle("CTWindow1")

        # Initialize QProcess
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    def run_script(self):
        if not self.query_input.text():
            QMessageBox.warning(self, "Warning", "Please enter a query.")
            return
        
        self.status_label.setText("Status: Running...")
        self.setDisabled(True)

        program = 'python3'
        arguments = ['src/windows/CT/Ominis-OSINT/ominis.py', '-q', self.query_input.text()]

        if self.language_checkbox.isChecked() and self.language_input.currentText():
            arguments += ['-l', f'lang_{self.language_input.currentText()}']
        if self.country_checkbox.isChecked() and self.country_input.currentText():
            arguments += ['-c', f'country{self.country_input.currentText()}']
        if self.start_date_checkbox.isChecked():
            arguments += ['-s', self.start_date_input.date().toString('MM/dd/yyyy')]
        if self.end_date_checkbox.isChecked():
            arguments += ['-e', self.end_date_input.date().toString('MM/dd/yyyy')]

        self.process.start(program, arguments)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode('utf-8').rstrip('\n')
        self.output_area.append(stdout)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode('utf-8').rstrip('\n')
        self.output_area.append(stderr)

    def process_finished(self):
        self.status_label.setText("Status: Finished")
        self.setDisabled(False)

