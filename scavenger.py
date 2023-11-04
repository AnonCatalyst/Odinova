import sys
import re
import json
import httpx
import urllib3
import urllib.parse
import asyncio
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QPalette

# Disable urllib3 warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load social platform patterns from a JSON file
with open("src/social_platforms.json", "r") as json_file:
    social_platforms = json.load(json_file)

found_social_profiles = set()
found_forum_pages = set()


class GoogleSearchError(Exception):
    pass


class WebSearchGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.query = None
        self.result_text = QTextEdit()
        self.error_text = QTextEdit()
        self.social_profiles_text = QTextEdit()
        self.forum_pages_text = QTextEdit()
        self.query_input = QLineEdit()
        self.num_results_input = QLineEdit()
        self.status_label = QLabel("❌")  # Initial status: Red X
        self.status_label.setStyleSheet("color: red; font-size: 20px;")

        # Set the initial status to "Inactive"
        self.set_status_icon("Inactive: ", "❌")

        # Create the event loop once
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 1000, 600)  # Set the initial window size

        layout = QVBoxLayout()

        # Create a tab widget
        tabs = QTabWidget()

        # Create tabs for results, errors, social profiles, forum pages
        results_tab = QWidget()
        errors_tab = QWidget()
        social_profiles_tab = QWidget()
        forum_pages_tab = QWidget()

        # Add the tabs to the tab widget
        tabs.addTab(results_tab, "Results")
        tabs.addTab(errors_tab, "Errors")
        tabs.addTab(social_profiles_tab, "Social Profiles")
        tabs.addTab(forum_pages_tab, "Forum Pages")

        # Set layouts for tabs
        results_layout = QVBoxLayout(results_tab)
        errors_layout = QVBoxLayout(errors_tab)
        social_profiles_layout = QVBoxLayout(social_profiles_tab)
        forum_pages_layout = QVBoxLayout(forum_pages_tab)

        # Add widgets to the layouts
        results_layout.addWidget(self.result_text)
        errors_layout.addWidget(self.error_text)
        social_profiles_layout.addWidget(self.social_profiles_text)
        forum_pages_layout.addWidget(self.forum_pages_text)

        # Add layouts to the corresponding tabs
        results_tab.setLayout(results_layout)
        errors_tab.setLayout(errors_layout)
        social_profiles_tab.setLayout(social_profiles_layout)
        forum_pages_tab.setLayout(forum_pages_layout)

        # Add the tab widget to the main layout
        layout.addWidget(tabs)

        # Create input fields and search button
        input_layout = QHBoxLayout()
        label_query = QLabel("Enter your query:")
        input_layout.addWidget(label_query)
        input_layout.addWidget(self.query_input)

        label_num_results = QLabel("Enter the number of results:")
        input_layout.addWidget(label_num_results)
        input_layout.addWidget(self.num_results_input)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.run_search)
        input_layout.addWidget(search_button)

        layout.addLayout(input_layout)
        layout.addWidget(self.status_label, alignment=Qt.AlignTop | Qt.AlignRight)  # Status label

        self.setLayout(layout)
        self.setWindowTitle("Scavenger - Osint Tool")

        # Set the background color and border style for the input boxes
        self.result_text.setStyleSheet("color: #00FFFF; background-color: #303030; border: 1px solid #FF0000;")
        self.query_input.setStyleSheet("background-color: #303030; color: white; border: 1px solid #FF0000;")
        self.num_results_input.setStyleSheet("background-color: #303030; color: white; border: 1px solid #FF0000;")

        # Set the style for the search button
        search_button.setStyleSheet("background-color: black; color: #FF0000; border: 1px solid #000000;")

    def run_search(self):
        self.set_status_icon("Running: ", "🔰")

        self.query = self.query_input.text()
        num_results = int(self.num_results_input.text()) if self.num_results_input.text().isdigit() else 10

        try:
            self.loop.run_until_complete(self.main_async(num_results))
        except Exception as e:
            print("Error during search:", e)
            self.set_status_icon("Inactive: ", "❌")
        else:
            self.set_status_icon("Finished: ", "🔱")
        #finally:
            # No need to close the loop here

    def set_status_icon(self, text, icon):
        full_text = f"{text} {icon}"
        self.status_label.setText(full_text)
        self.status_label.setStyleSheet(
            f"QLabel {{ color: gray; font-size: 12px; }}"
            f"QLabel::before {{ content: '{icon}'; color: red; display: inline-block; }}"
        )

    async def make_request_async(self, url):
        try:
            headers = {"User-Agent": UserAgent().random}
            async with httpx.AsyncClient(timeout=30, headers=headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except httpx.RequestError as e:
            self.error_text.setStyleSheet("color: #FF0000;")
            self.error_text.append(f"Error making request to {url}: {e}")
            raise GoogleSearchError(f"Error making request to {url}: {e}")

    def find_social_profiles(self, url):
        profiles = []
        for platform, pattern in social_platforms.items():
            match = re.search(pattern, url)
            if match:
                profile_url = match.group(0)
                profiles.append({"platform": platform, "profile_url": profile_url})

        if self.is_potential_forum(url):
            profiles.append({"platform": "Forum", "profile_url": url})

        return profiles

    def is_potential_forum(self, url):
        potential_forum_keywords = ["forum", "community", "discussion", "board", "chat", "hub"]
        url_parts = urllib.parse.urlparse(url)
        path = url_parts.path.lower()

        # Check for specific forum-related keywords in the URL path
        path_keywords = [keyword for keyword in potential_forum_keywords if keyword in path]

        # Adjust the condition based on your specific criteria
        return len(path_keywords) >= 2

    def extract_mentions(self, text, query):
        mention_pattern = rf"\b{re.escape(query)}\b"
        mentions = re.findall(mention_pattern, text, re.IGNORECASE)
        return len(mentions)

    async def main_async(self, num_results):
        # Clear previous results
        self.result_text.clear()
        self.error_text.clear()
        self.social_profiles_text.clear()
        self.forum_pages_text.clear()

        retry_count = 0

        async with httpx.AsyncClient(verify=False) as client:
            total_results_to_fetch = min(300, num_results)

            for start_index in range(0, total_results_to_fetch, 10):
                google_search_url = f"https://www.google.com/search?q={self.query}&start={start_index}"

                try:
                    response = await self.make_request_async(google_search_url)

                    if response is None:
                        raise GoogleSearchError("No response from Google Search")

                    soup = BeautifulSoup(response, "html.parser")
                    search_results = soup.find_all("div", class_="tF2Cxc")

                    if not search_results:
                        self.error_text.setStyleSheet("color: #FF0000;")
                        self.error_text.append(f"No more results found for the query '{self.query}'")
                        break

                    for index, result in enumerate(search_results, start=start_index + 1):
                        title = result.find("h3")
                        url = result.find("a")["href"] if result.find("a") else None

                        if title and url:
                            # Cyan color for titles
                            title_text = f"🔍 {index}. Title: {title.text}"
                            self.result_text.setStyleSheet("color: #00FFFF; background-color: #303030; border: 1px solid #FF0000;")
                            self.result_text.append(title_text)

                            # White color for URLs
                            url_text = f"   🌐 URL: {url}"
                            self.result_text.setStyleSheet("color: white; background-color: #303030; border: 1px solid #FF0000;")
                            self.result_text.append(url_text)

                            text_to_check = f"{title.text} {url}"
                            mention_count = self.extract_mentions(text_to_check, self.query)

                            if mention_count > 0:
                                # Black color for detection messages
                                detection_text = f"   🚨 '{self.query}' Detected in Title/Url: {url}"
                                self.result_text.setStyleSheet("color: white; background-color: #303030; border: 1px solid #FF0000;")
                                self.result_text.append(detection_text)

                                # Add to social profiles text
                                self.add_social_profile(index, url)

                            social_profiles = self.find_social_profiles(url)
                            if social_profiles:
                                for profile in social_profiles:
                                    self.add_social_profile(index, profile['profile_url'])

                            QApplication.processEvents()  # Allow the GUI to handle events

                            await asyncio.sleep(1)  # Introduce a short delay between iterations

                except GoogleSearchError as error:
                    self.error_text.setStyleSheet("color: #FF0000;")
                    self.error_text.append(f"🚫 Error during Google Search: {error}. Retrying in 5 seconds...")
                    await asyncio.sleep(5)

    def add_social_profile(self, index, profile_url):
        if profile_url not in found_social_profiles:
            if "forum" in profile_url.lower():
                # Add to forum pages text
                self.forum_pages_text.setStyleSheet("color: #00FF00; background-color: #303030; border: 1px solid #FF0000;")
                self.forum_pages_text.append(f"🌐 {index}. Forum: {profile_url}")
                found_forum_pages.add(profile_url)
            else:
                # Add to social profiles text
                self.social_profiles_text.setStyleSheet("color: #00FF00; background-color: #303030; border: 1px solid #FF0000;")
                self.social_profiles_text.append(f"🌐 {index}. {profile_url}")
            found_social_profiles.add(profile_url)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qp = QPalette()
    qp.setColor(QPalette.ButtonText, Qt.red)
    qp.setColor(QPalette.WindowText, Qt.white)
    qp.setColor(QPalette.Window, Qt.black)
    qp.setColor(QPalette.Button, Qt.black)
    app.setPalette(qp)
    app.setStyle("Fusion")
    app.setWindowIcon(QtGui.QIcon('img/icon_photo.png'))

    gui = WebSearchGUI()
    gui.show()
    sys.exit(app.exec_())
