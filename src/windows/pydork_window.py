from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QHBoxLayout
from PyQt6.QtCore import Qt
from pydork.engine import SearchEngine

class PyDorkWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyDork Tool")
        self.setStyleSheet("color: white; background-color: #1e1e1e;")
        
        layout = QVBoxLayout(self)
        
        # Adding description
        description_text = (
            "<h2 style='color: #ff4444;'>PyDork Tool</h2>"
            "<p>PyDork is a powerful tool for scraping and listing text and image searches "
            "on various search engines including Google, Bing, DuckDuckGo, Baidu, and Yahoo Japan.</p>"
            "<p><b>How to use:</b></p>"
            "<ul>"
            "<li>Enter your search query in the input field below.</li>"
            "<li>Click the <b>Search</b> button to perform the search.</li>"
            "<li>Results will be displayed in the text area below.</li>"
            "</ul>"
        )
        description_label = QLabel(self)
        description_label.setText(description_text)
        description_label.setOpenExternalLinks(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Search input field
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter your search query")
        self.search_input.setStyleSheet("background-color: #2e2e2e; color: white; padding: 5px; border: 1px solid #ff4444;")
        search_layout.addWidget(self.search_input)

        # Search button
        search_button = QPushButton("Search", self)
        search_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #000000;
                padding: 5px 10px;
                background-color: #1e1e1e;
                color: white;
            }
            QPushButton:hover { background-color: #2e2e2e; }
            QPushButton:pressed { background-color: #3e3e3e; }
            QPushButton:focus { outline: none; }
        """)
        search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # Result display area
        self.result_area = QTextEdit(self)
        self.result_area.setReadOnly(True)
        self.result_area.setStyleSheet("background-color: #2e2e2e; color: white; border: 2px solid #000000;")
        layout.addWidget(self.result_area)

    def perform_search(self):
        query = self.search_input.text()
        if query:
            search_engine = SearchEngine()
            search_engine.set('google')
            search_result = search_engine.search(query)
            results_text = "\n".join(f"{res}" for res in search_result)
            self.result_area.setText(results_text)
        else:
            self.result_area.setText("Please enter a search query.")
