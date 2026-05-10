import sys
import concurrent.futures
import logging
import random
import threading
import time
from colorama import Fore, Style, init
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import argparse
from requests.exceptions import RequestException

# Initialize colorama for colored output
init(autoreset=True)

# Set up logging
logging.basicConfig(filename='src/logs/username_search.log', level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Set up file for saving results
results_file = open("Results/username-search_results.txt", "w")

# Keep track of visited URLs to prevent duplicates
visited_urls = set()
visited_html_content = set()
visited_urls_lock = threading.Lock()
file_lock = threading.Lock()

def build_profile_url(base_url: str, username: str) -> str:
    if username.lower() in base_url.lower():
        return base_url

    # Handle profile templates that end with markers such as '@', '=' or ':'.
    if base_url.endswith(("/", "=", ":", "@", "~")):
        return f"{base_url}{username}"

    return f"{base_url.rstrip('/')}/{username}"


def search_username_on_url(username: str, url: str, include_titles=True, include_descriptions=True, include_html_content=True, request_timeout=12):
    """Run the search and return a list of output lines (never prints directly)."""
    global visited_urls, visited_html_content
    buf = []
    try:
        url = build_profile_url(url, username)

        with visited_urls_lock:
            if url in visited_urls:
                buf.append(f"{Fore.YELLOW}⚠️ {Fore.RED}Skipping duplicate URL: {Fore.WHITE}{url}")
                return buf
            visited_urls.add(url)

        session = HTMLSession()
        try:
            # Keep a small jitter, but avoid large delays that make scans feel stuck.
            time.sleep(random.uniform(0.15, 0.6))
            response = session.get(url, timeout=request_timeout)
        finally:
            session.close()

        if response.status_code == 200:
            with visited_urls_lock:
                if response.html.raw_html in visited_html_content:
                    buf.append(f"{Fore.YELLOW}⚠️ {Fore.RED}Skipping duplicate HTML content for URL: {Fore.WHITE}{url}")
                    return buf
                visited_html_content.add(response.html.raw_html)

            buf.append(f"{Fore.CYAN}🔍 {Fore.BLUE}{username} {Fore.RED}| {Fore.YELLOW}[{Fore.GREEN}✅{Fore.YELLOW}]{Fore.WHITE} URL{Fore.YELLOW}: {Fore.LIGHTGREEN_EX}{url}{Fore.WHITE} {response.status_code}")

            # Always check for query in URL, title, description, and HTML content
            buf.extend(build_query_detection(username, url, response.html.raw_html))

            # Write results to file
            write_to_file(username, url, response.status_code, response.html.raw_html, include_titles, include_descriptions, include_html_content)

            # Collect HTML content lines if requested
            if include_titles or include_descriptions or include_html_content:
                buf.extend(build_html_lines(response.html.raw_html, url, username, include_titles, include_descriptions, include_html_content))

        # Skip processing for non-200 status codes
    except RequestException as re:
        logging.info(f"Request failed/timed out for {username} on {url}: {re}")
    except UnicodeEncodeError as ue:
        logging.error(f"UnicodeEncodeError occurred while printing to console for {username} on {url}: {ue}")
    except Exception as e:
        logging.error(f"Error occurred while searching for {username} on {url}: {e}")
    return buf

def build_query_detection(username, url, html_content):
    """Return a list of output lines for query detection (does not print)."""
    lines = []
    query_detected = False
    try:
        # Check if username is detected in URL
        if username.lower() in url.lower():
            query_detected = True

        # Check if username is detected in HTML content
        if html_content and username.lower() in html_content.decode('utf-8').lower():
            lines.append(f"{Fore.YELLOW}🔸 {Fore.LIGHTBLACK_EX}Query detected in 'HTML content'{Fore.RED}... {Fore.WHITE}")
            query_detected = True

        # Check if username is detected in meta description
        soup = BeautifulSoup(html_content, 'html.parser')
        meta_description = soup.find("meta", attrs={"name": "description"})
        description = meta_description['content'] if meta_description else ""
        if username.lower() in description.lower():
            lines.append(f"{Fore.YELLOW}🔸 {Fore.LIGHTBLACK_EX}Query detected in 'description'{Fore.RED}... {Fore.WHITE}")
            query_detected = True

        # Check if username is detected in title
        title = soup.title.get_text(strip=True) if soup.title else ""
        if username.lower() in title.lower():
            lines.append(f"{Fore.YELLOW}🔸 {Fore.LIGHTBLACK_EX}Query detected in 'title'{Fore.RED}... {Fore.WHITE}")
            query_detected = True

        if not query_detected:
            lines.append(f"{Fore.YELLOW}🔸 Query not detected in URL, title, description, or HTML content for URL: {Fore.WHITE}{url}")

    except Exception as e:
        logging.error(f"Error occurred while checking for query in URL, title, description, or HTML content for URL: {url}: {e}")
    return lines

def write_to_file(username, url, status_code, html_content, include_titles=True, include_descriptions=True, include_html_content=True):
    try:
        with file_lock:
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
                html_content_str = html_content.decode('utf-8')
                results_file.write(f"HTML Content:\n{html_content_str}\n")
            results_file.write("\n")
    except Exception as e:
        logging.error(f"Error occurred while writing to file for {username} on {url}: {e}")

def build_html_lines(html_content, url, query, include_titles=True, include_descriptions=True, include_html_content=True):
    """Return a list of output lines for HTML display (does not print)."""
    lines = []
    try:
        if not html_content:
            lines.append(f"{Fore.YELLOW}HTML Content for URL {Fore.WHITE}{url}:{Fore.YELLOW} Empty")
            return lines

        soup = BeautifulSoup(html_content, 'html.parser')
        if include_titles:
            title = soup.title.get_text(strip=True) if soup.title else "No title found"
            if query.lower() in title.lower():
                lines.append(f"{Fore.YELLOW}🔸 TITLE: {Fore.WHITE}{title}")
        if include_descriptions:
            meta_description = soup.find("meta", attrs={"name": "description"})
            description = meta_description['content'] if meta_description else "No meta description found"
            if query.lower() in description.lower():
                lines.append(f"{Fore.YELLOW}🔸 DESCRIPTION: {Fore.WHITE}{description}")

        if include_html_content:
            lines.append(f"{Fore.YELLOW}🔸 HTML Content for URL {Fore.WHITE}{url}:{Fore.YELLOW}")
            # Decode bytes to string
            html_content_str = html_content.decode('utf-8')
            # Show a snippet for readability
            snippet_length = 300  # Adjust as needed
            html_snippet = html_content_str[:snippet_length] + ("..." if len(html_content_str) > snippet_length else "")
            lines.extend([f"{Fore.CYAN}{line}" for line in html_snippet.split("\n")])

    except Exception as e:
        logging.error(f"Error occurred while parsing HTML content for URL {url}: {e}")
    return lines

def main(username, include_titles, include_descriptions, include_html_content, request_timeout):
    print(f"\n    {Fore.CYAN}ＡＬＩＡＳＴＯＲＭ{Style.RESET_ALL}\n")

    with open("src/windows/CT/AliaStorm/src/urls.txt", "r") as f:
        url_list = [x.strip() for x in f.readlines()]

    if not username:
        print("❌ Error: Username cannot be empty.")
        return

    total = len(url_list)
    completed = 0
    output_lock = threading.Lock()
    stall_after_seconds = max(6, min(15, request_timeout))
    stall_update_interval_seconds = 5

    max_workers = min(24, max(8, total))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(
                search_username_on_url,
                username,
                url,
                include_titles,
                include_descriptions,
                include_html_content,
                request_timeout,
            ): url
            for url in url_list
        }
        pending = set(future_to_url)
        last_completion_at = time.monotonic()
        last_stall_update_at = 0.0

        while pending:
            done, pending = concurrent.futures.wait(
                pending,
                timeout=1.0,
                return_when=concurrent.futures.FIRST_COMPLETED,
            )

            now = time.monotonic()
            idle_for = now - last_completion_at
            if not done:
                if idle_for >= stall_after_seconds and (now - last_stall_update_at) >= stall_update_interval_seconds:
                    with output_lock:
                        print(
                            f"{Fore.LIGHTBLACK_EX}...still scanning ({completed}/{total} completed, waiting {int(idle_for)}s for next response){Style.RESET_ALL}",
                            flush=True,
                        )
                    last_stall_update_at = now
                continue

            for future in done:
                buf = future.result() or []
                with output_lock:
                    completed += 1
                    # Flush all buffered lines for this URL atomically.
                    for line in buf:
                        print(line)
                last_completion_at = time.monotonic()

    print(f"\n{Fore.GREEN}✅ Scan complete. {Fore.WHITE}{total} URLs processed for username '{Fore.CYAN}{username}{Fore.WHITE}'.{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search for a username across multiple URLs.')
    parser.add_argument('username', type=str, help='The username to search for')
    parser.add_argument('--include_titles', action='store_true', help='Include titles in the output')
    parser.add_argument('--include_descriptions', action='store_true', help='Include descriptions in the output')
    parser.add_argument('--include_html_content', action='store_true', help='Include HTML content in the output')
    parser.add_argument('--request_timeout', type=int, default=12, help='Per-request timeout in seconds (default: 12)')

    args = parser.parse_args()

    try:
        main(args.username, args.include_titles, args.include_descriptions, args.include_html_content, args.request_timeout)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        # Close the results file
        results_file.close()
