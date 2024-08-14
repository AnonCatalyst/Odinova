import sys
import concurrent.futures
import threading
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTextEdit, QLabel, QMessageBox, QStatusBar, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal
import requests
from requests.exceptions import RequestException
from fake_useragent import UserAgent
import logging

class WebScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.base_urls = {
            "Google": "https://www.google.com/search?q=",
            "DuckDuckGo": "https://html.duckduckgo.com/html/?q=",
            "StartPage": "https://www.startpage.com/do/dsearch?query=",
        }
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_random_user_agent(self):
        try:
            return self.ua.random
        except Exception as e:
            logging.warning(f"UserAgent could not be generated: {e}")
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def fetch(self, url):
        headers = {
            'User-Agent': self.get_random_user_agent()
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)  # Reduced timeout
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None

    def search_engine(self, query, engine):
        if not query.strip():
            logging.warning("Empty query provided.")
            return engine, []

        url = self.base_urls.get(engine)
        if not url:
            logging.error(f"Search engine '{engine}' is not supported.")
            return engine, []

        search_url = f"{url}{query}"
        search_urls = [f"{search_url}&start={i}" for i in range(0, 101, 10)]
        results = []

        # Fetch results in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.fetch, search_url) for search_url in search_urls]
            for future in concurrent.futures.as_completed(futures):
                page = future.result()
                if page:
                    results.append(page)

        return engine, results

    def run_search(self, query, engines):
        if not engines:
            logging.warning("No search engines provided.")
            return {}

        results = {}
        for engine in engines:
            engine_results = self.search_engine(query, engine)
            results[engine_results[0]] = engine_results[1]
        return results

class SearchThread(QThread):
    results_ready = pyqtSignal(dict)
    status_update = pyqtSignal(str)

    def __init__(self, query, engines, scraper):
        super().__init__()
        self.query = query
        self.engines = engines
        self.scraper = scraper

    def run(self):
        self.status_update.emit("Searching...")
        results = self.scraper.run_search(self.query, self.engines)
        self.results_ready.emit(results)
        self.status_update.emit("Search completed.")

class CTWindow3(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebHound")

        self.scraper = WebScraper()

        # Layout setup
        main_layout = QVBoxLayout()
        form_layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        # Query input
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter your query")
        form_layout.addWidget(QLabel("Query:"))
        form_layout.addWidget(self.query_input)

        # Checkboxes for search engines
        self.checkboxes = {}
        for engine in self.scraper.base_urls.keys():
            checkbox = QCheckBox(engine)
            self.checkboxes[engine] = checkbox
            input_layout.addWidget(checkbox)

        # Date range input
        input_layout.addWidget(QLabel("Date Range:"))
        self.date_range_input = QLineEdit()
        self.date_range_input.setPlaceholderText("Date range (optional, e.g., 'past 24 hours')")
        input_layout.addWidget(self.date_range_input)

        # Language input
        input_layout.addWidget(QLabel("Language:"))
        self.language_input = QLineEdit()
        self.language_input.setPlaceholderText("Language code (optional, e.g., 'en')")
        input_layout.addWidget(self.language_input)

        # Country input
        input_layout.addWidget(QLabel("Country:"))
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Country code (optional, e.g., 'US')")
        input_layout.addWidget(self.country_input)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        form_layout.addWidget(self.search_button)

        # Results output
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        form_layout.addWidget(QLabel("Results:"))
        form_layout.addWidget(self.results_output)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        form_layout.addWidget(self.status_bar)

        # Set layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

    def perform_search(self):
        query = self.query_input.text()
        engines = [engine for engine, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        date_range = self.date_range_input.text()
        language = self.language_input.text()
        country = self.country_input.text()

        if not query:
            QMessageBox.warning(self, "Input Error", "Query is required.")
            return

        if not engines:
            QMessageBox.warning(self, "Input Error", "At least one search engine must be selected.")
            return

        self.results_output.clear()
        self.update_status("Starting search...")

        # Start the search in a separate thread
        self.search_thread = SearchThread(query, engines, self.scraper)
        self.search_thread.results_ready.connect(self.display_results)
        self.search_thread.status_update.connect(self.update_status)
        self.search_thread.start()

    def display_results(self, results):
        self.results_output.clear()
        if not results:
            self.results_output.append("No results found.")
            return

        visited_links = set()
        for engine, pages in results.items():
            self.results_output.append(f"Results from {engine}:")
            for page in pages:
                if page:
                    soup = BeautifulSoup(page, 'html.parser')
                    for item in soup.select("div.tF2Cxc, div.result, li"):
                        link = item.find("a", href=True)
                        if link:
                            link_url = link['href']
                            if link_url not in visited_links:
                                visited_links.add(link_url)
                                self.results_output.append(f"Link: {link_url}")

    def update_status(self, message):
        self.status_label.setText(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CTWindow3()
    window.show()
    sys.exit(app.exec())
