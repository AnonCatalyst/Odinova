import sys
import requests
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent
import platform
import psutil
from colorama import Fore, Style, init
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QCheckBox
from PyQt6.QtCore import QThread, pyqtSignal
import time

# Initialize colorama
init(autoreset=True)

class ConsoleConfig:
    # Console styles
    BOLD = Style.BRIGHT
    END = Style.RESET_ALL

class Config:
    ERROR_CODE = -1
    SUCCESS_CODE = 0
    MIN_DATA_RETRIEVE_LENGTH = 1
    USE_PROXY = False

    SEARCH_ENGINE_URL = "https://ahmia.fi/search/?q="
    PROXY_API_URLS = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite",
        "https://www.proxy-list.download/api/v1/get?type=https",
        "https://www.proxy-list.download/api/v1/get?type=http"
    ]

class ProxyManager:
    def __init__(self):
        self.proxies = []

    def update_proxies(self):
        all_proxies = set()
        for url in Config.PROXY_API_URLS:
            try:
                response = requests.get(url)
                response.raise_for_status()  # Check for HTTP errors
                all_proxies.update(line.strip() for line in response.text.splitlines() if line.strip())
            except requests.RequestException as e:
                print(f"[!] Error fetching proxies from {url}: {e}")
        self.proxies = ["http://" + proxy for proxy in all_proxies]

    def get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None

class DepthSearch:
    def __init__(self):
        self.user_agent = UserAgent()
        self.session = requests.Session()  # Use session for persistent connections
        self.proxy_manager = ProxyManager()

    def search(self, query, amount):
        headers = {'User-Agent': self.user_agent.random}
        result_text = ""

        if Config.USE_PROXY:
            self.proxy_manager.update_proxies()  # Update proxies before starting the search

        proxies_used = 0
        results_found = 0

        while results_found < amount:
            if Config.USE_PROXY:
                proxy = self.proxy_manager.get_random_proxy()
                if proxy:
                    self.session.proxies.update({"http": proxy})

            try:
                response = self.session.get(Config.SEARCH_ENGINE_URL + query, headers=headers, timeout=10)
                response.raise_for_status()  # Ensure we handle HTTP errors

                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.find(id='ahmiaResultsPage')
                result_items = results.find_all('li', class_='result')

                titles = [item.find('p').text if item.find('p') else None for item in result_items]
                urls = [item.find('cite').text if item.find('cite') else None for item in result_items]

                if len(urls) >= Config.MIN_DATA_RETRIEVE_LENGTH:
                    for i in range(len(urls)):
                        url = urls[i]
                        title = titles[i] if i < len(titles) else None

                        output = f"{ConsoleConfig.BOLD}{Fore.LIGHTGREEN_EX}URL:{Fore.WHITE} {url}\n"
                        if title:  # Only print if title is available
                            output += f"\t{ConsoleConfig.BOLD}Title:{Fore.LIGHTBLUE_EX} {title}\n"
                        output += ConsoleConfig.END
                        result_text += output
                        results_found += 1
                        if results_found >= amount:
                            break
                else:
                    result_text += f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}No results found.{ConsoleConfig.END}\n"

                # Mimic human behavior with random delays between requests
                time.sleep(random.uniform(1, 3))
                
                proxies_used += 1
                if Config.USE_PROXY and proxies_used >= len(self.proxy_manager.proxies):
                    result_text += f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}Ran out of proxies.{ConsoleConfig.END}\n"
                    break

            except requests.RequestException as e:
                result_text += f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}Request failed: {e}{ConsoleConfig.END}\n"
                if Config.USE_PROXY:
                    self.proxy_manager.update_proxies()  # Update proxies on failure

        if results_found < amount:
            result_text += f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}Not enough results found after using all proxies.{ConsoleConfig.END}\n"
        
        return result_text

class SearchThread(QThread):
    results_ready = pyqtSignal(str)

    def __init__(self, query, amount, use_proxy):
        super().__init__()
        self.query = query
        self.amount = amount
        self.use_proxy = use_proxy

    def run(self):
        Config.USE_PROXY = self.use_proxy
        searcher = DepthSearch()
        result_text = searcher.search(self.query, self.amount)
        self.results_ready.emit(result_text)

class CTWindow4(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('CTWindow4 GUI')
        layout = QVBoxLayout()
        
        self.query_input = QLineEdit(self)
        self.query_input.setPlaceholderText("Enter the query")
        layout.addWidget(QLabel("Query:"))
        layout.addWidget(self.query_input)

        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Enter the number of results to retrieve (default: 25)")
        layout.addWidget(QLabel("Number of Results:"))
        layout.addWidget(self.amount_input)

        self.proxy_checkbox = QCheckBox("Use proxy for increased anonymity")
        layout.addWidget(self.proxy_checkbox)

        self.search_button = QPushButton('Search')
        self.search_button.clicked.connect(self.start_search)
        layout.addWidget(self.search_button)

        self.results_text_edit = QTextEdit(self)
        self.results_text_edit.setReadOnly(True)
        layout.addWidget(self.results_text_edit)

        self.setLayout(layout)

    def start_search(self):
        query = self.query_input.text().strip()
        amount_str = self.amount_input.text().strip()
        use_proxy = self.proxy_checkbox.isChecked()

        amount = 25
        if amount_str.isdigit():
            amount = int(amount_str)

        if query:
            self.results_text_edit.setPlainText("Searching...")
            self.search_thread = SearchThread(query, amount, use_proxy)
            self.search_thread.results_ready.connect(self.update_results)
            self.search_thread.start()
        else:
            self.results_text_edit.setPlainText(f"{ConsoleConfig.BOLD}{Fore.LIGHTRED_EX}No query arguments were passed. Please supply a query to search.{ConsoleConfig.END}")

    def update_results(self, result_text):
        self.results_text_edit.setPlainText(result_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CTWindow()
    window.show()
    sys.exit(app.exec())
