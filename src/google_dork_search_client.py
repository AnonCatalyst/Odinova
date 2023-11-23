import requests
import json
import os
import cloudscraper
from bs4 import BeautifulSoup
from colorama import Fore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea

class InfoLookupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Info Lookup Tool')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        label = QLabel(self.logo())
        layout.addWidget(label)

        self.input_label = QLabel("Enter IP, Phone, Email, or VIN:")
        layout.addWidget(self.input_label)

        self.input_entry = QLineEdit(self)
        layout.addWidget(self.input_entry)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.result_text)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def logo(self):
        return f''' {Fore.WHITE}
      ... Your logo text here ...
'''

    def get_info(self, cmd):
        scraper = cloudscraper.create_scraper()
        url = f'https://thatsthem.com/ip/{cmd}'
        cookies = dict(__stripe_mid='replace_with_actual_value',
                       __stripe_sid='replace_with_actual_value',
                       PHPSESSID='replace_with_actual_value',
                       remember='replace_with_actual_value')

        path = scraper.get(url, cookies=cookies).text
        soup = BeautifulSoup(path, 'lxml')

        result = f'''
{Fore.WHITE}𝗧𝗔𝗥𝗚𝗘𝗧        : {Fore.CYAN}{cmd}\n
-------------------------------'''

        # Your parsing logic here...

        return result

    def on_submit(self):
        cmd = self.input_entry.text()
        result = self.get_info(cmd)
        self.result_text.setPlainText(result)

if __name__ == '__main__':
    app = QApplication([])
    window = InfoLookupApp()
    window.show()
    app.exec_()
