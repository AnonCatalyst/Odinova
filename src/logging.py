from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTextEdit, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QCheckBox
from PyQt6.QtGui import QIcon, QTextCursor, QAction
from PyQt6.QtCore import Qt, QDateTime, QFile, QTextStream

class LoggingWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.interaction_logs = QTextEdit()
        self.interaction_logs.setReadOnly(True)
        self.interaction_logs.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555;
                font-size: 12px;
                color: #f0f0f0;
                padding: 5px;
            }
        """)

        self.error_logs = QTextEdit()
        self.error_logs.setReadOnly(True)
        self.error_logs.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555;
                font-size: 12px;
                color: #f0f0f0;
                padding: 5px;
            }
        """)

        self.tabs.addTab(self.interaction_logs, "Interaction Logs")
        self.tabs.addTab(self.error_logs, "ERROR Logs")

        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self.clear_logs)
        clear_button.setIcon(QIcon.fromTheme("edit-clear"))

        save_button = QPushButton("Save Logs")
        save_button.clicked.connect(self.save_logs)
        save_button.setIcon(QIcon.fromTheme("document-save"))

        self.log_interaction_checkbox = QCheckBox("Log UI Interactions")
        self.log_interaction_checkbox.setChecked(True)  # Default to logging interactions
        self.log_interaction_checkbox.stateChanged.connect(self.toggle_interaction_logs)

        button_layout = QHBoxLayout()
        button_layout.addWidget(clear_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(self.log_interaction_checkbox)
        button_layout.addStretch()

        layout.addWidget(self.tabs)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def toggle_interaction_logs(self, state):
        if state == Qt.CheckState.Checked:
            self.log_interaction_checkbox.setChecked(True)
        else:
            self.log_interaction_checkbox.setChecked(False)

    def log_interaction(self, message):
        if self.log_interaction_checkbox.isChecked():
            self._log_to_tab(self.interaction_logs, message)

    def log_warning(self, message):
        self._log_to_tab(self.error_logs, f"WARNING: {message}")

    def log_error(self, message):
        self._log_to_tab(self.error_logs, f"ERROR: {message}")

    def _log_to_tab(self, tab, message):
        timestamp = QDateTime.currentDateTime().toString(Qt.DateFormat.ISODateWithMs)
        log_entry = f"[{timestamp}] {message}"
        tab.append(log_entry)
        tab.moveCursor(QTextCursor.MoveOperation.End)

    def clear_logs(self):
        self.interaction_logs.clear()
        self.error_logs.clear()

    def save_logs(self):
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("Text files (*.txt)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            if not file_path.endswith(".txt"):
                file_path += ".txt"
            if QFile.exists(file_path):
                ret = QMessageBox.warning(self, "File Exists", f"The file {file_path} already exists. Do you want to overwrite it?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if ret == QMessageBox.StandardButton.No:
                    return
            self._save_logs_to_file(file_path)

    def _save_logs_to_file(self, file_path):
        with QFile(file_path) as file:
            if not file.open(QFile.OpenMode.WriteOnly | QFile.OpenMode.Text):
                QMessageBox.critical(self, "Error", f"Could not write to file:\n{file_path}")
                return
            text_stream = QTextStream(file)
            text_stream.setCodec("UTF-8")
            text_stream << "== Interaction Logs ==\n\n"
            text_stream << self.interaction_logs.toPlainText() << "\n\n"
            text_stream << "== ERROR Logs ==\n\n"
            text_stream << self.error_logs.toPlainText() << "\n\n"
        QMessageBox.information(self, "Logs Saved", f"Logs saved to:\n{file_path}")

