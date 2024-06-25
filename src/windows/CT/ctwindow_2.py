import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QTextEdit, QGroupBox, QCheckBox, QMessageBox
from PyQt6.QtCore import QProcess, Qt

class CTWindow2(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTWindow 2")
        self.setGeometry(100, 100, 600, 400)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Username input
        self.username_label = QLabel("Enter Username:")
        layout.addWidget(self.username_label)

        self.username_input = QTextEdit()
        self.username_input.setFixedHeight(30)  # Limit height for single-line input
        layout.addWidget(self.username_input)

        # Options group box
        self.options_groupbox = QGroupBox("Options")
        self.options_layout = QVBoxLayout(self.options_groupbox)

        self.chk_include_titles = QCheckBox("Include Titles")
        self.options_layout.addWidget(self.chk_include_titles)

        self.chk_include_descriptions = QCheckBox("Include Descriptions")
        self.options_layout.addWidget(self.chk_include_descriptions)

        self.chk_include_html_content = QCheckBox("Include HTML Content")
        self.options_layout.addWidget(self.chk_include_html_content)

        layout.addWidget(self.options_groupbox)

        # Button to run aliastorm.py
        self.btn_run_aliastorm = QPushButton("Run AliasStorm")
        self.btn_run_aliastorm.clicked.connect(self.start_aliastorm)
        layout.addWidget(self.btn_run_aliastorm)

        # Status indicators
        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        # Output display area
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)

        self.setLayout(layout)

        # QProcess for running aliastorm.py
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.finished.connect(self.handle_finished)

    def start_aliastorm(self):
        username = self.username_input.toPlainText().strip()
        include_titles = self.chk_include_titles.isChecked()
        include_descriptions = self.chk_include_descriptions.isChecked()
        include_html_content = self.chk_include_html_content.isChecked()

        # Prepare command to execute aliastorm.py
        program = "python3"  # Assuming 'python3' is in PATH
        script_path = "src/windows/CT/AliaStorm/aliastorm.py"
        args = [username]
        if include_titles:
            args.append("--include_titles")
        if include_descriptions:
            args.append("--include_descriptions")
        if include_html_content:
            args.append("--include_html_content")

        # Start the process
        self.output_display.clear()
        self.set_status("Running...")
        try:
            self.process.start(program, [script_path] + args)
        except Exception as e:
            self.show_error_message(f"Error starting process: {str(e)}")
            self.set_status("Error")

    def handle_output(self):
        output = self.process.readAllStandardOutput().data().decode("utf-8", "ignore").strip()
        if output:
            self.output_display.append(output)

    def handle_error(self):
        error = self.process.readAllStandardError().data().decode("utf-8", "ignore").strip()
        if error:
            self.output_display.append(f"Error: {error}")

    def handle_finished(self):
        exit_code = self.process.exitCode()
        if exit_code == 0:
            self.set_status("Finished successfully")
        else:
            self.set_status(f"Finished with error. Exit code {exit_code}")

    def set_status(self, message):
        self.status_label.setText(f"Status: {message}")

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec()

