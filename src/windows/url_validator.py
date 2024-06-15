from PyQt6.QtGui import QValidator
from PyQt6.QtCore import QUrl
import requests

class URLValidator(QValidator):
    def validate(self, url):
        url = url.strip()
        if url == "":
            return QValidator.Intermediate, url

        # Check URL syntax
        if not QUrl.fromUserInput(url).isValid():
            return QValidator.Invalid, url

        # Check if URL exists (returns a 404 status)
        try:
            response = requests.head(url)
            if response.status_code == 404:
                return QValidator.Invalid, url
        except Exception:
            # Handle network errors or other exceptions
            return QValidator.Intermediate, url

        return QValidator.Acceptable, url