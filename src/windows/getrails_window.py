from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QComboBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from getrails import go_gle, go_duck, go_onion

class SearchThread(QThread):
    search_finished = pyqtSignal(str)

    def __init__(self, term, engine):
        super().__init__()
        self.term = term
        self.engine = engine

    def run(self):
        if self.engine == "Google":
            result = go_gle(self.term)
        elif self.engine == "DuckDuckGo":
            result = go_duck(self.term)
        elif self.engine == "Onion":
            result = go_onion(self.term)
        else:
            result = "Error: Invalid search engine."
        self.search_finished.emit(str(result))

class GetRailsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Get Rails Search")
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 2px solid black;")
        self.layout = QVBoxLayout(self)

        # Description
        self.description_label = QLabel(
            "The <b>Getrails Python library</b> is a specialized tool designed for Open-Source Intelligence (OSINT) "
            "gathering and Dork hacking, providing a programmable interface to conduct searches on Google, DuckDuckGo, "
            "and Onion networks."
        )
        self.description_label.setStyleSheet("color: #ffffff;")
        self.description_label.setWordWrap(True)
        self.layout.addWidget(self.description_label)

        # Search term input
        self.term_label = QLabel("Search Term:")
        self.term_label.setStyleSheet("color: #ffffff;")
        self.term_input = QLineEdit()
        self.layout.addWidget(self.term_label)
        self.layout.addWidget(self.term_input)

        # Search engine selection
        self.engine_label = QLabel("Search Engine:")
        self.engine_label.setStyleSheet("color: #ffffff;")
        self.engine_combobox = QComboBox()
        self.engine_combobox.addItems(["Google", "DuckDuckGo", "Onion"])
        self.layout.addWidget(self.engine_label)
        self.layout.addWidget(self.engine_combobox)

        # Run button
        self.run_button = QPushButton("Run Search")
        self.run_button.setStyleSheet("color: #ffffff; background-color: #007acc;")
        self.run_button.clicked.connect(self.run_search)
        self.layout.addWidget(self.run_button)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #ffffff;")
        self.layout.addWidget(self.status_label)

        # Output display
        self.output_label = QLabel("Output:")
        self.output_label.setStyleSheet("color: #ffffff;")
        self.layout.addWidget(self.output_label)
        self.output_text = QTextEdit()
        self.output_text.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: 1px solid black;")
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

    def run_search(self):
        term = self.term_input.text()
        engine = self.engine_combobox.currentText()

        if not term:
            self.output_text.setText("Error: Search term is required.")
            return

        self.status_label.setText("Searching...")
        self.search_thread = SearchThread(term, engine)
        self.search_thread.search_finished.connect(self.update_output)
        self.search_thread.finished.connect(self.search_finished)
        self.search_thread.start()

    def update_output(self, result):
        self.status_label.setText("Ready")
        self.output_text.setText(result)

    def search_finished(self):
        self.status_label.setText("Ready")
