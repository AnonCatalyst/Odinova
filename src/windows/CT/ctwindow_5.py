from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel,
    QProgressBar, QTabWidget, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from aiohttp import ClientSession, ClientError, ClientResponseError, hdrs
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urlparse, urljoin
import sys
import asyncio
import re
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrawlerThread(QThread):
    update_progress = pyqtSignal(int)
    update_results = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, url, output_dir):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self._running = True

    def run(self):
        asyncio.run(self.crawl_website())

    def stop(self):
        self._running = False

    async def fetch_html(self, url, session, retries=3):
        try:
            user_agent = UserAgent().random
            headers = {hdrs.USER_AGENT: user_agent}
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                return await response.text()
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
        except ClientResponseError as e:
            logger.error(f"ClientResponseError fetching {url}: {e.status}")
        except ClientError as e:
            logger.error(f"ClientError fetching {url}: {e}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")

        if retries > 0:
            await asyncio.sleep(2 ** (3 - retries))
            return await self.fetch_html(url, session, retries - 1)
        else:
            return None

    def extract_emails(self, html):
        emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html))
        return emails

    def get_links(self, html, base_url):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            internal_links = set()
            external_links = set()
            parsed_base_url = urlparse(base_url)
            base_domain = parsed_base_url.netloc

            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                parsed_url = urlparse(absolute_url)
                
                if parsed_url.scheme in ('http', 'https'):
                    if parsed_url.netloc == base_domain:
                        internal_links.add(absolute_url)
                    else:
                        external_links.add((absolute_url, base_url))

            return internal_links, external_links
        except Exception as e:
            logger.error(f"Error parsing links from {base_url}: {e}")
            return set(), set()

    def extract_title_and_description(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No title"
        description = soup.find('meta', attrs={'name': 'description'})
        description = description.get('content', '').strip() if description else "No description"
        return title, description

    async def crawl_website(self):
        async with ClientSession() as session:
            visited_urls = set()
            all_external_links = set()
            all_internal_titles = {}
            all_internal_descriptions = {}
            all_external_titles = {}
            all_external_descriptions = {}

            def save_results(data):
                os.makedirs(self.output_dir, exist_ok=True)
                with open(os.path.join(self.output_dir, f"{urlparse(self.url).netloc}_results.json"), 'w') as f:
                    json.dump(data, f, indent=4)

            async def crawl(url):
                if not self._running:
                    return
                
                if url in visited_urls:
                    return
                
                visited_urls.add(url)
                
                html = await self.fetch_html(url, session)
                if not html:
                    return
                
                title, description = self.extract_title_and_description(html)
                
                internal_links, external_links = self.get_links(html, url)
                
                all_emails = self.extract_emails(html)

                new_internal_links = set()
                new_external_links = set()

                for link in internal_links:
                    try:
                        internal_html = await self.fetch_html(link, session)
                        if internal_html:
                            internal_title, internal_description = self.extract_title_and_description(internal_html)
                            all_internal_titles[link] = internal_title
                            all_internal_descriptions[link] = internal_description

                            internal_soup = BeautifulSoup(internal_html, 'html.parser')
                            internal_base_url = urlparse(link)
                            for internal_link in internal_soup.find_all('a', href=True):
                                internal_absolute_url = urljoin(link, internal_link['href'])
                                internal_parsed_url = urlparse(internal_absolute_url)
                                if internal_parsed_url.scheme in ('https', 'http') and internal_parsed_url.netloc == internal_base_url.netloc:
                                    new_internal_links.add(internal_absolute_url)
                                else:
                                    new_external_links.add((internal_absolute_url, link))
                            
                    except Exception as e:
                        logger.error(f"Error extracting from internal link {link}: {e}")

                internal_links.update(new_internal_links)
                all_external_links.update(new_external_links)

                for ext_link, referring_url in external_links:
                    try:
                        external_html = await self.fetch_html(ext_link, session)
                        if external_html:
                            external_title, external_description = self.extract_title_and_description(external_html)
                            all_external_titles[ext_link] = external_title
                            all_external_descriptions[ext_link] = external_description
                    except Exception as e:
                        logger.error(f"Error extracting from external link {ext_link}: {e}")

                crawl_results = {
                    'url': url,
                    'title': title,
                    'description': description,
                    'internal_links': list(internal_links),
                    'external_links': list(all_external_links),
                    'emails': list(all_emails),
                    'meta_data': {}
                }

                save_results(crawl_results)
                self.update_results.emit({
                    'internal_titles': all_internal_titles,
                    'internal_descriptions': all_internal_descriptions,
                    'external_titles': all_external_titles,
                    'external_descriptions': all_external_descriptions
                })
                self.status_update.emit(f"Crawling in progress... Processed: {url}")

            try:
                await crawl(self.url)
                self.update_results.emit({
                    'internal_titles': all_internal_titles,
                    'internal_descriptions': all_internal_descriptions,
                    'external_titles': all_external_titles,
                    'external_descriptions': all_external_descriptions
                })
                self.status_update.emit("Crawling completed successfully.")
            except Exception as e:
                self.error_signal.emit(f"Error in crawling process: {e}")
                self.status_update.emit(f"Error: {e}")

class CTWindow5(QMainWindow):
    status_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTWindow5: WebDiver")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter target URL")
        self.layout.addWidget(self.url_input)

        self.output_dir_button = QPushButton("Select Output Directory")
        self.output_dir_button.clicked.connect(self.select_output_dir)
        self.layout.addWidget(self.output_dir_button)

        self.start_button = QPushButton("Start Crawling")
        self.start_button.clicked.connect(self.start_crawling)
        self.layout.addWidget(self.start_button)

        self.status_label = QLabel("Status: Not started")
        self.layout.addWidget(self.status_label)

        self.results_tabs = QTabWidget()
        self.results_tabs.addTab(QTextEdit(), "Results")
        self.results_tabs.addTab(QTextEdit(), "Internal Links")
        self.results_tabs.addTab(QTextEdit(), "External Links")
        self.layout.addWidget(self.results_tabs)

        self.crawler_thread = None
        self.output_dir = ""

        self.status_update.connect(self.update_status)

    def select_output_dir(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_name:
            self.output_dir = dir_name

    def start_crawling(self):
        if self.crawler_thread and self.crawler_thread.isRunning():
            self.stop_crawling()

        url = self.url_input.text()
        if url and self.output_dir:
            self.crawler_thread = CrawlerThread(url, self.output_dir)
            self.crawler_thread.status_update.connect(self.update_status)
            self.crawler_thread.update_results.connect(self.display_results)
            self.crawler_thread.error_signal.connect(self.update_status)
            self.crawler_thread.start()
            self.update_status("Crawling started...")
        else:
            self.update_status("Please provide a URL and select an output directory.")

    def stop_crawling(self):
        if self.crawler_thread:
            self.crawler_thread.stop()
            self.crawler_thread.wait()
            self.update_status("Crawling stopped.")

    def update_status(self, status_message):
        self.status_label.setText(f"Status: {status_message}")

    def display_results(self, results):
        self.results_tabs.setCurrentIndex(0)
        results_text = json.dumps(results, indent=4)
        self.results_tabs.widget(0).setPlainText(results_text)
        self.results_tabs.widget(1).setPlainText(json.dumps(results.get('internal_titles', {}), indent=4))
        self.results_tabs.widget(2).setPlainText(json.dumps(results.get('external_titles', {}), indent=4))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CTWindow5()
    window.show()
    sys.exit(app.exec())
