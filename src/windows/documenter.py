import sys
import os
import threading
import markdown
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QComboBox, QLineEdit, QMessageBox, QTabWidget, QHBoxLayout, QFileDialog, QStatusBar
from PyQt6.QtCore import pyqtSignal, pyqtSlot

class Documenter(QWidget):
    open_document = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Add buttons layout
        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        # Add button to add more document tabs
        self.add_tab_button = QPushButton("Add Document")
        self.add_tab_button.clicked.connect(self.add_document_tab)
        self.buttons_layout.addWidget(self.add_tab_button)

        # Add delete button
        self.delete_tab_button = QPushButton("Delete Document")
        self.delete_tab_button.clicked.connect(self.delete_current_tab)
        self.buttons_layout.addWidget(self.delete_tab_button)

        # Add Save button
        self.save_button = QPushButton("Save All")
        self.save_button.clicked.connect(self.save_documents)
        self.buttons_layout.addWidget(self.save_button)

        # Add Open button
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file_dialog)
        self.buttons_layout.addWidget(self.open_button)

        # Add Status Bar
        self.status_bar = QStatusBar()
        self.layout.addWidget(self.status_bar)

        # Add initial tab for first document
        self.add_document_tab()

    def add_document_tab(self):
        # Create a new tab for a document
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        text_edit = QTextEdit()
        tab_layout.addWidget(text_edit)

        file_widget_layout = QVBoxLayout()
        tab_layout.addLayout(file_widget_layout)

        file_type_combo = QComboBox()
        file_type_combo.addItems(["doc", "txt", "md"])  # Added Markdown
        file_widget_layout.addWidget(file_type_combo)

        file_name_input = QLineEdit()
        file_name_input.setPlaceholderText("Enter file name...")
        file_widget_layout.addWidget(file_name_input)

        self.tab_widget.addTab(tab, f"Document {self.tab_widget.count()}")
        self.tab_widget.setCurrentWidget(tab)

    def delete_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.removeTab(current_index)

    def save_documents(self):
        docs_directory = "src/docs"
        if not os.path.exists(docs_directory):
            os.makedirs(docs_directory)

        for i in range(self.tab_widget.count()):
            tab_widget = self.tab_widget.widget(i)
            text_edit = tab_widget.findChild(QTextEdit)
            file_type_combo = tab_widget.findChild(QComboBox)
            file_name_input = tab_widget.findChild(QLineEdit)

            content = text_edit.toPlainText()
            file_type = file_type_combo.currentText()
            file_name = file_name_input.text()

            if not file_name:
                QMessageBox.warning(self, "Warning", "Please enter a file name for all documents.")
                return

            if content:
                file_path = os.path.join(docs_directory, f"{file_name}.{file_type.lower()}")
                try:
                    with open(file_path, "w") as file:
                        file.write(content)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file {file_path}: {e}")
                    return

        QMessageBox.information(self, "Success", "Documents saved successfully.")

    def open_file_dialog(self):
        docs_directory = "src/docs"
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open File", docs_directory)
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()

            file_name = os.path.basename(file_path)
            file_name = os.path.splitext(file_name)[0]

            text_edit = QTextEdit()
            text_edit.setPlainText(content)
            self.tab_widget.addTab(text_edit, file_name)
            self.tab_widget.setCurrentWidget(text_edit.parentWidget())

            self.status_bar.showMessage(f"File '{file_name}' loaded successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file {file_path}: {e}")
