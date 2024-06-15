from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from subprocess import Popen, PIPE

class SearchWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = Popen(self.command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            self.finished.emit(stdout.decode())
        else:
            self.finished.emit(f"Error: {stderr.decode()}")

class UnderworldQuestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UnderworldQuest")
        self.setStyleSheet("QWidget {background-color: #202020;}")  # Apply dark theme to the window

        self.layout = QVBoxLayout(self)

        self.description_label = QLabel("<b>UnderworldQuest</b> is a powerful Python3 script designed to explore the depths of the web. With UnderworldQuest, users can effortlessly input search terms (queries) and unveil a trove of deep web sites associated with their query. Unlock the mysteries of the digital underworld with UnderworldQuest. Your gateway to the hidden web awaits!")
        self.description_label.setWordWrap(True)
        self.layout.addWidget(self.description_label)
        self.description_label.setStyleSheet("color: #DFA301;")  # Change text color to gold

        self.query_label = QLabel("Query:")
        self.layout.addWidget(self.query_label)

        self.query_input = QLineEdit()
        self.layout.addWidget(self.query_input)
        self.query_input.setStyleSheet("border: 2px solid #000000; background-color: #303030; color: #FFFFFF; padding: 5px;")  # Apply dark theme to input box

        self.amount_label = QLabel("Amount (optional):")
        self.layout.addWidget(self.amount_label)

        self.amount_input = QLineEdit()
        self.layout.addWidget(self.amount_input)
        self.amount_input.setStyleSheet("border: 2px solid #000000; background-color: #303030; color: #FFFFFF; padding: 5px;")  # Apply dark theme to input box

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.run_search)
        self.buttons_layout.addWidget(self.search_button)

        self.search_proxy_button = QPushButton("Search with Proxy")
        self.search_proxy_button.clicked.connect(lambda: self.run_search(proxy=True))
        self.buttons_layout.addWidget(self.search_proxy_button)

        self.status_label = QLabel("Ready")
        self.layout.addWidget(self.status_label)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #00FF00;")  # Green color for status label
        self.status_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.layout.addWidget(self.results_text)
        self.results_text.setStyleSheet("border: 2px solid #000000; background-color: #303030; color: #FFFFFF; padding: 5px;")  # Apply dark theme to results text box

        self.worker = None  # Initialize worker variable

    def run_search(self, proxy=False):
        if self.worker and self.worker.isRunning():  # Check if a worker is already running
            self.status_label.setText("Previous search still running...")
            return

        query = self.query_input.text().strip()
        amount = self.amount_input.text().strip()

        if not query:
            self.status_label.setText("Please enter a query.")
            return

        self.status_label.setText("Searching...")  # Update status label to indicate search is in progress

        command = ["python3", "src/windows/ottools/UnderworldQuest/UnderworldQuest.py", "--query", query]
        if amount:
            command.extend(["--amount", amount])
        if proxy:
            command.append("-p")

        self.worker = SearchWorker(command)
        self.worker.finished.connect(self.update_results)
        self.worker.finished.connect(lambda: self.status_label.setText("Search completed."))  # Update status label when search is completed
        self.worker.start()

    def update_results(self, result):
        self.results_text.setText(result)
