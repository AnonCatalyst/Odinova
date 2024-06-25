import sys
import concurrent.futures
import logging
import random
import time
from colorama import Fore, Style, init
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import argparse

# Initialize colorama for colored output
init(autoreset=True)

# Set up logging
logging.basicConfig(filename='src/username_search.log', level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Set up file for saving results
results_file = open("Results/username-search_results.txt", "w")

# Keep track of visited URLs to prevent duplicates
visited_urls = set()
visited_html_content = set()

def search_username_on_url(username: str, url: str, include_titles=True, include_descriptions=True, include_html_content=True):
    global visited_urls, visited_html_content
    try:
        if username.lower() not in url.lower():
            url += f'/{username}' if url.endswith('/') else f'/{username}'

        if url in visited_urls:
            print(f"{Fore.YELLOW}⚠️ {Fore.RED}Skipping duplicate URL: {Fore.WHITE}{url}")
            return

        visited_urls.add(url)

        session = HTMLSession()
        time.sleep(random.uniform(1, 3))  # Introduce a random delay to mimic human behavior
        response = session.get(url)

        if response.status_code == 200:
            if response.html.raw_html in visited_html_content:
                print(f"{Fore.YELLOW}⚠️ {Fore.RED}Skipping duplicate HTML content for URL: {Fore.WHITE}{url}")
                return

            visited_html_content.add(response.html.raw_html)

            print(f"{Fore.CYAN}🔍 {Fore.BLUE}{username} {Fore.RED}| {Fore.YELLOW}[{Fore.GREEN}✅{Fore.YELLOW}]{Fore.WHITE} URL{Fore.YELLOW}: {Fore.LIGHTGREEN_EX}{url}{Fore.WHITE} {response.status_code}")

            # Always check for query in URL, title, description, and HTML content
            print_query_detection(username, url, response.html.raw_html)

            # Write results to file
            write_to_file(username, url, response.status_code, response.html.raw_html, include_titles, include_descriptions, include_html_content)

            # Print HTML content with organized formatting if requested
            if include_titles or include_descriptions or include_html_content:
                print_html(response.html.raw_html, url, username, include_titles, include_descriptions, include_html_content)

        else:
            # Skip processing for non-200 status codes
            return
    except UnicodeEncodeError as ue:
        logging.error(f"UnicodeEncodeError occurred while printing to console for {username} on {url}: {ue}")
    except Exception as e:
        logging.error(f"Error occurred while searching for {username} on {url}: {e}")

def print_query_detection(username, url, html_content):
    query_detected = False
    try:
        # Check if username is detected in URL
        if username.lower() in url.lower():
            query_detected = True

        # Check if username is detected in HTML content
        if html_content and username.lower() in html_content.decode('utf-8').lower():
            print(f"{Fore.YELLOW}🔸 {Fore.LIGHTBLACK_EX}Query detected in 'HTML content'{Fore.RED}... {Fore.WHITE}")
            query_detected = True

        # Check if username is detected in meta description
        soup = BeautifulSoup(html_content, 'html.parser')
        meta_description = soup.find("meta", attrs={"name": "description"})
        description = meta_description['content'] if meta_description else ""
        if username.lower() in description.lower():
            print(f"{Fore.YELLOW}🔸 {Fore.LIGHTBLACK_EX}Query detected in 'description'{Fore.RED}... {Fore.WHITE}")
            query_detected = True

        # Check if username is detected in title
        title = soup.title.get_text(strip=True) if soup.title else ""
        if username.lower() in title.lower():
            print(f"{Fore.YELLOW}🔸 {Fore.LIGHTBLACK_EX}Query detected in 'title'{Fore.RED}... {Fore.WHITE}")
            query_detected = True

        if not query_detected:
            print(f"{Fore.YELLOW}🔸 Query not detected in URL, title, description, or HTML content for URL: {Fore.WHITE}{url}")

    except Exception as e:
        logging.error(f"Error occurred while checking for query in URL, title, description, or HTML content for URL: {url}: {e}")

def write_to_file(username, url, status_code, html_content, include_titles=True, include_descriptions=True, include_html_content=True):
    try:
        results_file.write(f"Username: {username}\n")
        results_file.write(f"URL: {url}\n")
        results_file.write(f"Status Code: {status_code}\n")
        if include_titles:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.title.get_text(strip=True) if soup.title else "No title found"
            results_file.write(f"Title: {title}\n")
        if include_descriptions:
            meta_description = soup.find("meta", attrs={"name": "description"})
            description = meta_description['content'] if meta_description else "No meta description found"
            results_file.write(f"Description: {description}\n")
        if include_html_content:
            # Decode bytes to string
            html_content_str = html_content.decode('utf-8')
            results_file.write(f"HTML Content:\n{html_content_str}\n")
        results_file.write("\n")
    except Exception as e:
        logging.error(f"Error occurred while writing to file for {username} on {url}: {e}")

def print_html(html_content, url, query, include_titles=True, include_descriptions=True, include_html_content=True):
    try:
        if not html_content:
            print(f"{Fore.YELLOW}HTML Content for URL {Fore.WHITE}{url}:{Fore.YELLOW} Empty")
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        if include_titles:
            title = soup.title.get_text(strip=True) if soup.title else "No title found"
            if query.lower() in title.lower():
                print(f"{Fore.YELLOW}🔸 TITLE: {Fore.WHITE}{title}")
        if include_descriptions:
            meta_description = soup.find("meta", attrs={"name": "description"})
            description = meta_description['content'] if meta_description else "No meta description found"
            if query.lower() in description.lower():
                print(f"{Fore.YELLOW}🔸 DESCRIPTION: {Fore.WHITE}{description}")

        if include_html_content:
            print(f"{Fore.YELLOW}🔸 HTML Content for URL {Fore.WHITE}{url}:{Fore.YELLOW}")
            # Decode bytes to string
            html_content_str = html_content.decode('utf-8')
            # Print a snippet of the HTML content with line breaks for better readability
            snippet_length = 300  # Adjust as needed
            html_snippet = html_content_str[:snippet_length] + ("..." if len(html_content_str) > snippet_length else "")
            print("\n".join([f"{Fore.CYAN}{line}" for line in html_snippet.split("\n")]))

    except Exception as e:
        logging.error(f"Error occurred while parsing HTML content for URL {url}: {e}")

def main(username, include_titles, include_descriptions, include_html_content):
    print(f"\n    {Fore.CYAN}ＡＬＩＡＳＴＯＲＭ{Style.RESET_ALL}\n")

    with open("src/windows/CT/AliaStorm/src/urls.txt", "r") as f:
        url_list = [x.strip() for x in f.readlines()]

    if not username:
        print("❌ Error: Username cannot be empty.")
        return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(search_username_on_url, username, url, include_titles, include_descriptions, include_html_content) for url in url_list]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search for a username across multiple URLs.')
    parser.add_argument('username', type=str, help='The username to search for')
    parser.add_argument('--include_titles', action='store_true', help='Include titles in the output')
    parser.add_argument('--include_descriptions', action='store_true', help='Include descriptions in the output')
    parser.add_argument('--include_html_content', action='store_true', help='Include HTML content in the output')

    args = parser.parse_args()

    try:
        main(args.username, args.include_titles, args.include_descriptions, args.include_html_content)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        # Close the results file
        results_file.close()
