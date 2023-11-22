# usr.py

import requests
from urllib.parse import urljoin

def check_user_in_urls(target_username, urls):
    results = {}

    for url in urls:
        full_url = urljoin(url, target_username)

        try:
            response = requests.get(full_url, timeout=10)
            if response.status_code == 200:
                results[full_url] = "Username Found"
            else:
                results[full_url] = "Username Not Found"
        except requests.RequestException:
            results[full_url] = "Error"

    return results

