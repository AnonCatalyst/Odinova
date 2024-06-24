import argparse
import asyncio
import logging
import os
import random
import subprocess
import urllib3
from colorama import Fore, Style, init

# Import your modules for proxy handling and fetching Google results
from src.proxy_handler import scrape_proxies, validate_proxies
from src.tools_handler import fetch_google_results

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize colorama for colored output
init(autoreset=True)

DEFAULT_NUM_RESULTS = 500
MAX_RETRY_COUNT = 5

counter_emojis = ['🍻', '📑', '📌', '🌐', '🔰', '💀', '🔍', '📮', 'ℹ️', '📂', '📜', '📋', '📨', '🌟', '💫', '✨', '🔥', '🆔', '🎲']
emoji = random.choice(counter_emojis)  # Select a random emoji for the counter


async def run_command(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


async def main():
    args = parse_arguments()
    clear_screen()
    display_banner()

    proxies = await scrape_proxies()
    if not proxies:
        logger.error(f"{Fore.RED}No proxies scraped. Exiting...{Style.RESET_ALL}")
        return

    logger.info(f"{Fore.RED}[{Fore.GREEN}+{Fore.RED}]{Fore.WHITE} Beginning proxy validation for proxy rotation{Fore.RED}.{Fore.WHITE}\n")

    valid_proxies = await validate_proxies(proxies)
    if not valid_proxies:
        logger.error(f"{Fore.RED}No valid proxies found. Exiting...{Fore.WHITE}")
        return

    logger.info(f">{Fore.GREEN} Proxies validated successfully{Fore.RED}.{Fore.WHITE}\n")

    print(f"{Fore.RED}_" * 80 + "\n")

    await fetch_google_results(args.query, args.language, args.country, (args.start_date, args.end_date), valid_proxies)
    await asyncio.sleep(3)  # Introduce delay between requests



def parse_arguments():
    parser = argparse.ArgumentParser(description='Secure Web-Hunter')
    parser.add_argument('-q', '--query', type=str, required=True, help='The query to search')
    parser.add_argument('-l', '--language', type=str, help='The language code (e.g., "lang_en" for English)')
    parser.add_argument('-c', '--country', type=str, help='The country code (e.g., "countryUS" for United States)')
    parser.add_argument('-s', '--start_date', type=str, help='The start date for the date range (MM/DD/YYYY)')
    parser.add_argument('-e', '--end_date', type=str, help='The end date for the date range (MM/DD/YYYY)')
    return parser.parse_args()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_banner():
    print(
        f"""
{Fore.YELLOW} {Fore.WHITE}🇴‌🇲‌🇮‌🇳‌🇮‌🇸‌-🇴‌🇸‌🇮‌🇳‌🇹‌ {Fore.YELLOW}- {Fore.RED}[{Fore.WHITE}Secure Web-Hunter{Fore.RED}]
{Fore.RED} ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    {Fore.YELLOW}~ {Fore.CYAN}Developer{Fore.YELLOW}: {Fore.WHITE} AnonCatalyst {Fore.MAGENTA}<{Fore.RED}
    {Fore.RED}------------------------------------------
    {Fore.YELLOW}~ {Fore.CYAN}Github{Fore.YELLOW}:{Fore.BLUE} https://github.com/AnonCatalyst/{Fore.RED}
    {Fore.RED}------------------------------------------
    {Fore.YELLOW}~ {Fore.CYAN}Instagram{Fore.YELLOW}:{Fore.BLUE} https://www.instagram.com/istoleyourbutter/{Fore.RED}
    {Fore.RED}~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    {Fore.YELLOW}~ {Fore.CYAN}Website{Fore.YELLOW}:{Fore.BLUE} https://hard2find.dev/{Fore.RED}"""
    )


if __name__ == "__main__":
    asyncio.run(main())
