import sys
import re
import json
import httpx
import urllib3
import urllib.parse
import asyncio
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTabWidget, QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QStackedWidget, QStackedLayout, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
import serpapi
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
import time
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QLineEdit
import psutil
from src.inf import get_system_info
from PyQt5.QtCore import QObject, pyqtSignal
import subprocess
import os
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from src.usr import check_user_in_urls
import requests
from requests.exceptions import RequestException, ConnectionError, TooManyRedirects, SSLError
from colorama import Fore
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGraphicsBlurEffect
from PyQt5.QtCore import QTimer
import warnings
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QDesktopWidget, QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QImage, QDesktopServices
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtWidgets import QGridLayout

# Add these lines before the class definitions where the warnings occur
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure the logging module
logging.basicConfig(filename='src/maigret.log', level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

os.system("clear")


# Initialize UserAgent object
user_agent = UserAgent()
# Define headers with a fake user agent
headers = {
    'User-Agent': user_agent.random,
    'Accept-Language': 'en-US,en;q=0.5',
    # Add any other headers you may need
}
# Set up the 'header' variable
header = headers

# Disable urllib3 warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load social platform patterns from a JSON file
with open("src/social_platforms.json", "r") as json_file:
    social_platforms = json.load(json_file)

found_social_profiles = set()
found_forum_pages = set()



class GoogleSearchError(Exception):
    pass



class MaigretSearchThread(QThread):
    maigret_finished = pyqtSignal(str)
    log_message = pyqtSignal(str)

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.start_time = None

    def run(self):
        self.start_time = datetime.now()

        # Log the start of the Maigret process
        self.log_message.emit(f"Maigret process started for username: {self.username}")

        try:
            # Run the Maigret command with the inputted username
            command = f"python3 src/maigret/maigret.py {self.username} -a"
            result = os.popen(command).read()

            # Log the end of the Maigret process
            self.log_message.emit(f"Maigret process ended for username: {self.username}")

            # Log the duration of the Maigret process
            end_time = datetime.now()
            duration = end_time - self.start_time
            self.log_message.emit(f"Maigret process took {duration}")

            self.maigret_finished.emit(result)
        except Exception as e:
            error_message = f"Error in MaigretSearchThread: {str(e)}"
            self.log_message.emit(error_message)
            self.maigret_finished.emit(error_message)


class MaigretSearchGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.username_input = QLineEdit()
        self.maigret_result_text = QTextEdit()
        self.log_text = QTextEdit()

        self.maigret_thread = None  # Initialize maigret_thread as None

        self.maigret_timer = QTimer()
        self.maigret_timer.timeout.connect(self.update_maigret_status)
        # Set the interval to 15 seconds (15000 milliseconds)
        self.maigret_timer.start(15000)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        tab_widget = QTabWidget()

        # Create tabs
        maigret_tab = QWidget()
        log_tab = QWidget()

        tab_widget.addTab(maigret_tab, "Maigret Results")
        tab_widget.addTab(log_tab, "Logs")

        # Layouts for each tab
        maigret_layout = QVBoxLayout(maigret_tab)
        log_layout = QVBoxLayout(log_tab)

        # Maigret tab content
        label_username = QLabel("Enter target username:")
        maigret_layout.addWidget(label_username)
        maigret_layout.addWidget(self.username_input)

        search_button = QPushButton("- ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ꜱᴛᴀʀᴛ -")
        search_button.clicked.connect(self.run_maigret_search)
        maigret_layout.addWidget(search_button)

        maigret_layout.addWidget(self.maigret_result_text)

        # Log tab content
        log_layout.addWidget(self.log_text)

        # Set the background color and border style for the input boxes and result box
        for widget in [self.username_input, self.maigret_result_text, self.log_text]:
            widget.setStyleSheet("background-color: #303030; color: white; border: 1px solid #333333;")

        layout.addWidget(tab_widget)
        self.setLayout(layout)



    def run_maigret_search(self):
        username = self.username_input.text()
        if not username:
            QMessageBox.warning(self, "Warning", "Please enter a username.")
            return

        # Create an instance of the Maigret search thread and pass the username
        self.maigret_thread = MaigretSearchThread(username)
        self.maigret_thread.maigret_finished.connect(self.display_maigret_results)
        self.maigret_thread.log_message.connect(self.display_log)

        # Start the Maigret search thread
        self.maigret_thread.start()

        # Start the timer to update the Maigret status in the log every 15 seconds
        self.maigret_timer.start()

        self.display_maigret_results("""Searching with Maigret...
~~~~~~~~~~~~~~~~~~~~~~~~~
This can take a while depending on your network speed
the estimated wait time is around 5 to 7 minutes.""")
        print("""
        {Scavenger-Osint-GUI] User Interaction: (Maigret Usersearch) Started...
        - Esimated wait time is about 5 to 7 minutes!""")


    def update_maigret_status(self):
        if self.maigret_thread and self.maigret_thread.isRunning():
            # Calculate the duration and notify the user
            current_time = datetime.now()
            duration = current_time - self.maigret_thread.start_time
            self.display_log(f"Maigret is still running. Please wait. Duration: {duration}")
        else:
            # If the thread is not running, stop the timer
            self.maigret_timer.stop()

    def display_maigret_results(self, result):
        # Display the result in the Maigret results tab
        self.maigret_result_text.setPlainText(result)

    def display_log(self, log_message):
        # Display log messages in the "Logs" tab
        self.log_text.append(log_message)

    def closeEvent(self, event):
        # Save the Maigret results when the window is closed
        maigret_results = self.maigret_result_text.toPlainText()
        with open("reports/maigret_results.txt", "w") as f:
            f.write(maigret_results)
        event.accept()

    def showEvent(self, event):
        # Load the saved Maigret results when the window is shown
        try:
            with open("reports/maigret_results.txt", "r") as f:
                maigret_results = f.read()
                self.maigret_result_text.setPlainText(maigret_results)
        except FileNotFoundError:
            pass
        event.accept()
        os.system("rm -rf reports")
        
class UserSearchThread(QThread):
    # Add error signal
    search_result = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, username, url_list):
        super().__init__()
        self.username = username
        self.url_list = url_list

    def run(self):
        for url in self.url_list:
            url = urllib.parse.urljoin(url, self.username)
            try:
                s = requests.Session()
                s.headers.update(headers)
                response = s.get(url, allow_redirects=False, timeout=5)

                if response.status_code == 200 and self.username.lower() in response.text.lower():
                    result = f"• {self.username} | [✓] URL: {url} {response.status_code}"
                    # Emit the search result through the signal
                    self.search_result.emit(result)
            except (ConnectionError, TooManyRedirects, RequestException, SSLError, TimeoutError) as e:
                # Emit the error through the signal
                self.error.emit(f"Error during search for user in {url}: {str(e)}")
            except Exception as e:
                # Emit the error through the signal
                self.error.emit(f"Unexpected error during search for user in {url}: {str(e)}")
            finally:
                # Emit log message
                self.log.emit(f"Search for user in {url} completed.")

class UserSearchGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.username_input = QLineEdit()
        self.result_text = QTextEdit()
        self.error_text = QTextEdit()
        self.log_text = QTextEdit()
        self.search_thread = None  # Initialize search_thread as None


        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label_username = QLabel("Enter target username:")
        layout.addWidget(label_username)
        layout.addWidget(self.username_input)

        search_button = QPushButton("- ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ꜱᴛᴀʀᴛ -")
        search_button.clicked.connect(self.run_user_search)
        layout.addWidget(search_button)

        # Create a tab widget
        tabs = QTabWidget()

        # Create tabs for results, errors, and logging
        results_tab = QWidget()
        errors_tab = QWidget()
        log_tab = QWidget()

        # Add the tabs to the tab widget
        tabs.addTab(results_tab, "Results")
        tabs.addTab(errors_tab, "Errors")
        tabs.addTab(log_tab, "Logging")

        # Set layouts for tabs
        results_layout = QVBoxLayout(results_tab)
        errors_layout = QVBoxLayout(errors_tab)
        log_layout = QVBoxLayout(log_tab)

        # Add widgets to the layouts
        results_layout.addWidget(self.result_text)
        errors_layout.addWidget(self.error_text)
        log_layout.addWidget(self.log_text)

        # Set the background color for the text boxes in all tabs
        for text_edit in [self.result_text, self.error_text, self.log_text]:
            text_edit.setStyleSheet("background-color: #303030; color: white; border: 1px solid #333333;")

        # Add layouts to the corresponding tabs
        results_tab.setLayout(results_layout)
        errors_tab.setLayout(errors_layout)
        log_tab.setLayout(log_layout)

        # Add the tab widget to the main layout
        layout.addWidget(tabs)

        self.setLayout(layout)

        for widget in [self.username_input, self.result_text, self.error_text, self.log_text]:
            widget.setStyleSheet("background-color: #303030; color: white; border: 1px solid #333333;")

    def run_user_search(self):
        target_username = self.username_input.text()
        if not target_username:
            QMessageBox.warning(self, "Warning", "Please enter a target username.")
            return

        # Create an instance of the username search thread and pass the target_username and url_list
        url_list = self.load_urls_from_file()
        self.search_thread = UserSearchThread(target_username, url_list)
        self.search_thread.search_result.connect(self.display_username_search_result)
        self.search_thread.error.connect(self.display_error)
        self.search_thread.log.connect(self.display_log)

        # Start the search thread
        self.search_thread.start()

        self.display_username_search_result("Searching for user in URLs...")

    def display_username_search_result(self, result):
        self.result_text.append(result)

    def display_error(self, error):
        self.error_text.append(error)

    def display_log(self, log):
        self.log_text.append(log)

    def load_urls_from_file(self):
        try:
            with open("src/urls.txt", "r") as f:
                return [x.strip() for x in f.readlines()]
        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", "URLs file (src/urls.txt) not found.")
            return []


class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        
    def init_ui(self):
        main_layout = QVBoxLayout()

        # Create a QHBoxLayout for the widgets on the right side (image, name, and bio)
        right_layout = QHBoxLayout()

        # Create a QLabel for displaying the image
        image_label = QLabel(self)
        pixmap = QPixmap('img/discord.jpg')  # Replace 'img/profile_image.jpg' with the actual path to your image
        pixmap = pixmap.scaledToWidth(100)  # Set the desired width
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)  # Center the image

        # Create a QVBoxLayout for the right side (name and bio)
        text_layout = QVBoxLayout()

        # Create a QLabel for displaying the name
        name_label = QLabel('Odinova Osint GUI')
        name_label.setAlignment(Qt.AlignCenter)  # Center the text

        # Create a QTextEdit for displaying the bio
        bio_box = QTextEdit()
        bio_box.setReadOnly(True)
        bio_box.setStyleSheet("background-color: #303030; color: white; border: 1px solid #333333;")

        # Read content from bio.txt file and set it to the bio box
        try:
            with open('src/bio.txt', 'r') as file:
                bio_text = file.read()
                bio_box.setPlainText(bio_text)
        except FileNotFoundError:
            bio_box.setPlainText("Bio file not found.")

        # Add name and bio widgets to the text layout
        text_layout.addWidget(name_label)
        text_layout.addWidget(bio_box)

        # Add image and text layout to the right layout
        right_layout.addWidget(image_label)
        right_layout.addLayout(text_layout)

        # Add the right layout to the main layout
        main_layout.addLayout(right_layout)

        # Create a scrollable box for displaying system information
        info_box = QPlainTextEdit()
        info_box.setReadOnly(True)
        info_box.setStyleSheet("background-color: #303030; color: white; border: 1px solid #333333;")

        # Add the info box to the main layout
        main_layout.addWidget(info_box)

        self.setLayout(main_layout)

        # Get and display system information
        get_system_info(info_box)

####
        ### MainApp
####
        
class MainApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        os.system("clear")

    def init_ui(self):
        self.setGeometry(105, 100, 1100, 600)  # Set the initial window size

        layout = QVBoxLayout()
   
        # Create a side menu with buttons
        side_menu_layout = QVBoxLayout()
        side_menu_layout.setAlignment(Qt.AlignTop)
        side_menu_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to zero

        # Load the custom image
        custom_image_path = 'src/co2.png'
        custom_image = QtGui.QPixmap(custom_image_path)


        # Create a QLabel to display the custom image
        custom_image_label = QLabel()
        custom_image_label.setPixmap(custom_image.scaledToWidth(90))  # Set a fixed width (adjust as needed)
        custom_image_label.setAlignment(Qt.AlignCenter)  # Center the image

        # Create a separator line
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setFrameShadow(QFrame.Sunken)
        separator_line.setStyleSheet("background-color: cyan;")
        

        # Create the Home button
        home_button = HoverPushButton("★彡 𝙃𝙊𝙈𝙀 彡★")
        home_button.clicked.connect(self.show_home)
        web_search_button = HoverPushButton("𝙒𝙚𝙗 𝙎𝙚𝙖𝙧𝙘𝙝")
        web_search_button.clicked.connect(self.show_web_search)
        serpapi_button = HoverPushButton("𝙎𝙚𝙧𝙥𝘼𝙋𝙄")
        serpapi_button.clicked.connect(self.show_serpapi_search)
        user_search_button = HoverPushButton("𝙐𝙨𝙚𝙧 𝙎𝙚𝙖𝙧𝙘𝙝")
        user_search_button.clicked.connect(self.show_user_search)
        maigret_button = HoverPushButton("𝙈𝙖𝙞𝙜𝙧𝙚𝙩")
        maigret_button.clicked.connect(self.show_maigret_search)
        
        # Add a separator line
        separator_line1 = QFrame()
        separator_line1.setFrameShape(QFrame.VLine)
        separator_line1.setFrameShadow(QFrame.Sunken)
        separator_line1.setStyleSheet("background-color: #222222;")


        # Add widgets to the side menu layout
        side_menu_layout.addWidget(custom_image_label)  # Add the image label
        side_menu_layout.addWidget(separator_line)  # Add the separator line
        side_menu_layout.addWidget(home_button)
        side_menu_layout.addWidget(web_search_button)
        side_menu_layout.addWidget(serpapi_button)
        side_menu_layout.addWidget(user_search_button)
        side_menu_layout.addWidget(maigret_button)



        # Add a line border on the right side of the side menu
        side_menu_widget = QWidget()
        side_menu_widget.setLayout(side_menu_layout)
        side_menu_widget.setStyleSheet("border-top: 1px solid #333333; border-right: 1px solid #333333;")  # Darker gray line border

        # Create a stacked widget to manage different views
        self.stacked_widget = QStackedWidget()

        # Add the side menu and stacked widget to the main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(side_menu_widget)
        main_layout.addWidget(self.stacked_widget)

        layout.addLayout(main_layout)

        # Set up the web search and home views
        self.setup_web_search_view()
        self.setup_home_view()

        self.setLayout(layout)
        self.setWindowTitle("•._.••´¯``•.¸¸.•`        ꜱᴄᴀᴠᴇɴɢᴇʀ ᴏꜱɪɴᴛ ɢᴜɪ        `•.¸¸.•``¯´••._.•")
        self.show_web_search()  # Show the web search view by default


    def open_threat_map(self):
        # Open the web view of the specified URL in a new window
        web_view = QWebEngineView()
        web_view.setUrl(QUrl("https://threatmap.bitdefender.com/"))
        web_view.setWindowTitle("Threat Map")
        web_view.show()



    def setup_web_search_view(self):
        web_search_view = WebSearchGUI()
        self.stacked_widget.addWidget(web_search_view)
        

    def show_serpapi_search(self):
        serpapi_view = SerpapiSearchGUI()
        self.stacked_widget.addWidget(serpapi_view)
        self.stacked_widget.setCurrentWidget(serpapi_view)



    def setup_home_view(self):
        home_view = HomeWindow()
        self.stacked_widget.addWidget(home_view)
        # Automatically run the info gathering script when the Home view is set up

    def show_home(self):
        self.stacked_widget.setCurrentIndex(1)
       
    def show_web_search(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_user_search(self):
        user_search_view = UserSearchGUI()
        self.stacked_widget.addWidget(user_search_view)
        self.stacked_widget.setCurrentWidget(user_search_view)

    def setup_maigret_search_view(self):
        maigret_view = MaigretSearchGUI()
        self.stacked_widget.addWidget(maigret_view)

    def show_maigret_search(self):
        self.setup_maigret_search_view()
        self.stacked_widget.setCurrentIndex(self.stacked_widget.count() - 1)

class HoverPushButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(HoverPushButton, self).__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setStyleSheet(
            """
            HoverPushButton {
                background-color: black;
                color: white;
                border: 1px solid #333333; /* Added border with padding */
                padding: 8px; /* Adjusted padding for separation */
                text-align: left;
            }
            HoverPushButton:hover {
                background-color: black;
                border: 1px solid cyan; 
                color: cyan;
            }
            HoverPushButton:pressed {
                background-color: #002434;
                border: 1px solid cyan;
                padding: 10px;
            }
            """
        )

    def mousePressEvent(self, event):
        if self.isEnabled():
            self.animate_click_effect()
            self.clicked.emit()
        super().mousePressEvent(event)

    def animate_click_effect(self):
        original_geometry = self.geometry()

        # Define the target geometries for fade-in and fade-out
        fade_in_geometry = original_geometry.adjusted(-5, -5, 5, 5)
        fade_out_geometry = original_geometry

        # Set the duration of the animation in milliseconds
        duration = 200

        # Set easing curve for smooth animation
        easing_curve = QEasingCurve.InOutQuad

        # Create animation for position
        pos_animation = QPropertyAnimation(self, b"pos")
        pos_animation.setStartValue(original_geometry.topLeft())
        pos_animation.setEndValue(original_geometry.topLeft())
        pos_animation.setDuration(duration)
        pos_animation.setEasingCurve(easing_curve)

        # Create animation for size
        size_animation = QPropertyAnimation(self, b"size")
        size_animation.setStartValue(original_geometry.size())
        size_animation.setEndValue(original_geometry.size())
        size_animation.setDuration(duration)
        size_animation.setEasingCurve(easing_curve)

        # Create animation for geometry
        geometry_animation = QPropertyAnimation(self, b"geometry")
        geometry_animation.setStartValue(original_geometry)
        geometry_animation.setEndValue(original_geometry)
        geometry_animation.setDuration(duration)
        geometry_animation.setEasingCurve(easing_curve)

        # Start the animations
        pos_animation.start()
        size_animation.start()
        geometry_animation.start()

        # Connect the finished signal to reset the colors after the animation completes
        pos_animation.finished.connect(self.reset_colors)

    def reset_colors(self):
        self.setStyleSheet(
            """
            HoverPushButton {
                background-color: black;
                color: white;
                border: 1px solid #222222; /* Added border with padding */
                padding: 8px; /* Adjusted padding for separation */
                text-align: left;
            }
            HoverPushButton:hover {
                background-color: black;
                color: cyan;
            }
            HoverPushButton:pressed {
                background-color: green;
                color: black;
            }
            """
        )

class SerpapiSearchThread(QThread):
    search_finished = pyqtSignal(str)

    def __init__(self, token, query):
        super().__init__()
        self.token = token
        self.query = query

    def run(self):
        results = self.perform_serpapi_search(self.token, self.query)
        self.search_finished.emit(results)

    def perform_serpapi_search(self, token, query):
        params = {
            'api_key': token,
            'q': query,
            'json': 1,
        }

        search = serpapi.GoogleSearch(params)
        results = search.get_dict()

        return json.dumps(results, indent=2)


class SerpapiSearchGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.token_input = QLineEdit()
        self.query_input = QLineEdit()
        self.result_text = QTextEdit()

        # Create an instance of the thread
        self.search_thread = SerpapiSearchThread("", "")
        self.search_thread.search_finished.connect(self.display_serpapi_results)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label_token = QLabel("Enter your Serpapi Token:")
        layout.addWidget(label_token)
        layout.addWidget(self.token_input)

        label_query = QLabel("Enter your search query:")
        layout.addWidget(label_query)
        layout.addWidget(self.query_input)

        search_button = QPushButton("- ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ꜱᴛᴀʀᴛ -")
        search_button.clicked.connect(self.run_serpapi_search)
        layout.addWidget(search_button)
        layout.addWidget(self.result_text)

        # Add a Save button
        save_button = QPushButton("ꜱᴀᴠᴇ ᴀᴘɪ ᴋᴇʏ")
        save_button.clicked.connect(self.save_api_key)
        layout.addWidget(save_button)

        self.setLayout(layout)

        # Set the background color and border style for the input boxes
        for input_box in [self.token_input, self.query_input]:
            input_box.setStyleSheet("background-color: #303030; color: white; border: 1px solid #333333;")

        # Set the background color, text color, and border style for the result box
        self.result_text.setStyleSheet("background-color: #303030; color: white; border: 1px solid #333333;")

    def save_api_key(self):
        api_key = self.token_input.text()

        if api_key:
            with open("src/serpapi_api_key.json", "w") as json_file:
                json.dump({"api_key": api_key}, json_file)
                QMessageBox.information(self, "Success", "API Key saved successfully.")
        else:
            QMessageBox.warning(self, "Warning", "Please enter the Serpapi Token before saving.")
        
    def run_serpapi_search(self):
        token = self.token_input.text()
        query = self.query_input.text()

        if not token or not query:
            QMessageBox.warning(self, "Warning", "Please enter both Serpapi Token and search query.")
            return

        # Set the token and query for the search thread
        self.search_thread.token = token
        self.search_thread.query = query

        # Start the search thread
        self.search_thread.start()

    def display_serpapi_results(self, results):
        self.result_text.setPlainText(results)
        

class WebSearchGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.query = None
        self.result_text = QTextEdit()
        self.error_text = QTextEdit()
        self.social_profiles_text = QTextEdit()
        self.forum_pages_text = QTextEdit()
        self.mentions_text = QTextEdit()  # New QTextEdit widget for mentions
        self.actions_text = QTextEdit()  # New QTextEdit widget for actions
        self.query_input = QLineEdit()
        self.num_results_input = QLineEdit()
        self.status_label = QLabel("❌")  # Initial status: Red X
        self.status_label.setStyleSheet("color: cyan; font-size: 20px;")

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

        # Create tabs for results, errors, social profiles, forum pages, mentions, and actions
        results_tab = QWidget()
        errors_tab = QWidget()
        social_profiles_tab = QWidget()
        forum_pages_tab = QWidget()
        mentions_tab = QWidget()  # New tab for mentions
        actions_tab = QWidget()  # New tab for actions

        # Add the tabs to the tab widget
        tabs.addTab(results_tab, "Results")
        tabs.addTab(errors_tab, "Errors")
        tabs.addTab(social_profiles_tab, "Social Profiles")
        tabs.addTab(forum_pages_tab, "Forum Pages")
        tabs.addTab(mentions_tab, "Mentions")  # Add the mentions tab
        tabs.addTab(actions_tab, "Logging")  # Add the actions tab

        # Set layouts for tabs
        results_layout = QVBoxLayout(results_tab)
        errors_layout = QVBoxLayout(errors_tab)
        social_profiles_layout = QVBoxLayout(social_profiles_tab)
        forum_pages_layout = QVBoxLayout(forum_pages_tab)
        mentions_layout = QVBoxLayout(mentions_tab)  # Layout for the mentions tab
        actions_layout = QVBoxLayout(actions_tab)  # Layout for the actions tab

        # Add widgets to the layouts
        results_layout.addWidget(self.result_text)
        errors_layout.addWidget(self.error_text)
        social_profiles_layout.addWidget(self.social_profiles_text)
        forum_pages_layout.addWidget(self.forum_pages_text)
        mentions_layout.addWidget(self.mentions_text)  # Add the mentions text widget to the mentions layout
        actions_layout.addWidget(self.actions_text)  # Add the actions text widget to the actions layout

        # Set the background color for the text boxes in all tabs
        for text_edit in [self.result_text, self.error_text, self.social_profiles_text, self.forum_pages_text, self.mentions_text, self.actions_text]:
            text_edit.setStyleSheet("background-color: #303030; color: white; border: 1px solid #333333;")


        # Add layouts to the corresponding tabs
        results_tab.setLayout(results_layout)
        errors_tab.setLayout(errors_layout)
        social_profiles_tab.setLayout(social_profiles_layout)
        forum_pages_tab.setLayout(forum_pages_layout)
        mentions_tab.setLayout(mentions_layout)  # Set the layout for the mentions tab
        actions_tab.setLayout(actions_layout)  # Set the layout for the actions tab

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
        self.setWindowTitle("Odinova - Osint Tool")

        # Set the background color and border style for the input boxes
        self.result_text.setStyleSheet("color: black; background-color: #303030; border: 1px solid black;")
        self.query_input.setStyleSheet("background-color: #303030; color: white; border: 1px solid black;")
        self.num_results_input.setStyleSheet("background-color: #303030; color: white; border: 1px solid black;")

        # Set the style for the search button
        search_button.setStyleSheet("background-color: black; color: cyan; border: 1px solid black;")

    def run_search(self):
        self.log_action("Google Search started.")

        self.set_status_icon("Running: ", "🔰")

        self.query = self.query_input.text()
        num_results = int(self.num_results_input.text()) if self.num_results_input.text().isdigit() else 10

        try:
            self.loop.run_until_complete(self.main_async(num_results))
        except Exception as e:
            print("Error during Google search:", e)
            self.set_status_icon("Inactive: ", "❌")
        else:
            self.set_status_icon("Finished: ", "🔱")

        self.log_action("Google Search finished.")


    def alternative_forum_detection(self, url):
        # Add your alternative forum detection logic here
        # For example, check if the URL contains common forum software paths or patterns
        forum_software_paths = ["phpbb", "vbulletin", "invision", "mybb"]
        return any(path in url.lower() for path in forum_software_paths)

    def set_status_icon(self, text, icon):
        full_text = f"{text} {icon}"
        self.status_label.setText(full_text)
        self.status_label.setStyleSheet(
            f"QLabel {{ color: gray; font-size: 12px; }}"
            f"QLabel::before {{ content: '{icon}'; color: cyan; display: inline-block; }}"
        )

    async def make_request_async(self, url):
        try:
            self.log_action(f"Making request to {url}")
            headers = {"User-Agent": UserAgent().random}
            async with httpx.AsyncClient(timeout=30, headers=headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                self.log_action(f"Request successful: {url}")
                return response.text
        except httpx.RequestError as e:
            self.log_action(f"Error making request to {url}: {e}")
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
        potential_forum_keywords = ["forum", "community", "discussion", "board", "chat", "hub", "messageboard", "forumdisplay", "bbs", "phpbb"]
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
        self.mentions_text.clear()  # Clear mentions tab
        self.actions_text.clear()  # Clear actions tab

        retry_count = 0

        async with httpx.AsyncClient(verify=True) as client:
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
                            self.result_text.setStyleSheet("color: #00FFFF; background-color: #303030; border: 1px solid black;")
                            self.result_text.append(title_text)

                            # White color for URLs
                            url_text = f"   🌐 URL: {url}"
                            self.result_text.setStyleSheet("color: white; background-color: #303030; border: 1px solid black;")
                            self.result_text.append(url_text)

                            text_to_check = f"{title.text} {url}"
                            mention_count = self.extract_mentions(text_to_check, self.query)

                            # Check for forums using the first method
                            if self.is_potential_forum(url):
                                self.add_forum_page(index, url)

                            # Check for forums using the alternative method
                            if self.alternative_forum_detection(url):
                                self.add_forum_page(index, url)

                            if mention_count > 0:
                                # Black color for detection messages
                                detection_text = f"   🚨 '{self.query}' Detected in Title/Url: {url}"
                                self.result_text.setStyleSheet("color: white; background-color: #303030; border: 1px solid black;")
                                self.result_text.append(detection_text)

                                # Add to social profiles text
                                self.add_social_profile(index, url)

                                # Log the mention in the mentions tab
                                self.mentions_text.append(f"Mention in result {index}: {url}")

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
        # Check if the full URL is not in found_social_profiles
        if profile_url not in found_social_profiles:
            if "forum" in profile_url.lower():
                # Add to forum pages text
                self.forum_pages_text.setStyleSheet("color: #00FF00; background-color: #303030; border: 1px solid black;")
                self.forum_pages_text.append(f"🌐 {index}. Forum: {profile_url}")
                found_forum_pages.add(profile_url)
            else:
                # Add to social profiles text
                self.social_profiles_text.setStyleSheet("color: #00FF00; background-color: #303030; border: 1px solid black;")
                self.social_profiles_text.append(f"🌐 {index}. {profile_url}")
            found_social_profiles.add(profile_url)

            # Log the action in the actions tab
            self.log_action(f"Identified social profile: {profile_url}")

        # Track the index and URL in a dictionary
        url_index_dict = {url: index for url in found_social_profiles}

        # Clear the found_social_profiles set
        found_social_profiles.clear()

        # Update found_social_profiles with the unique URLs
        found_social_profiles.update(url_index_dict)



    def log_action(self, action):
        # Log an action in the actions tab
        self.actions_text.append(action)
        QApplication.processEvents()  # Allow the GUI to handle events

if __name__ == '__main__':
    app = QApplication(sys.argv)
    qp = QPalette()
    qp.setColor(QPalette.ButtonText, Qt.cyan)
    qp.setColor(QPalette.WindowText, Qt.white)
    qp.setColor(QPalette.Window, Qt.black)
    qp.setColor(QPalette.Button, Qt.black)
    app.setPalette(qp)
    app.setStyle("Fusion")
    app.setWindowIcon(QtGui.QIcon('img/icon_photo.jpg'))

    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
