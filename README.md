># Scavenger Osint GUI 🌐🕵️‍♂️

Scavenger is a Python-based Open Source Intelligence (OSINT) tool designed to perform web searches and extract relevant information from search results. It is equipped with a graphical user interface (GUI) using PyQt5, making it user-friendly and accessible.

🚀 Happy OSINTing! 🕵️‍♂️

<img src="img/screenshot.png" alt="Scavenger GUI Project - screenshot" width="550" height="300"/>
<img src="img/screenshot2.png" alt="Scavenger GUI Project - screenshot" width="550" height="300"/>

## Features

- **Web Search:** Utilizes Google Search to retrieve results based on a user-specified query.
- **Social Profile Detection:** Identifies potential social media profiles and forum pages related to the search results.
- **Keyword Mention Detection:** Detects mentions of a specified keyword in the search results' titles and URLs.
- **Asynchronous Processing:** Utilizes asyncio for asynchronous web requests, ensuring efficient and responsive searches.
- **User-Friendly GUI:** Intuitive graphical interface for easy interaction and result visualization.

## Requirements

- Python 3.7 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - `httpx`
  - `beautifulsoup4`
  - `fake_useragent`
  - `PyQt5`

## Usage

1. Clone the repository:

    ```bash
    git clone https://github.com/AnonCatalyst/Scavenger.git
    cd Scavenger
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the tool:

    ```bash
    python scavenger.py
    ```

4. Enter your search query and the number of results you want.

5. Click the "Search" button to initiate the OSINT search.

6. View the results in different tabs: Results, Errors, Social Profiles, Forum Pages.

![Watch the video](img/video.gif)

**Information Obtained**
    Discover online mentions of a query or username.
    Identify potential social profiles and forums.
    Enhance web searches with SerpApi for more accurate results.

**Why Ominis?**
    Ominis offers a unified solution for multiple OSINT tasks.
    Threading improves efficiency for username searches.
    SerpApi integration enhances web search capabilities.
    
### Digital Reconnaissance
Positioned as a robust solution for digital reconnaissance, Ominis OSINT Tools excels in gathering and analyzing publicly available information from online sources. The toolkit empowers users with the capability to navigate and extract valuable insights from the vast landscape of digital data.

### Targeted and Actionable Results
Ominis OSINT Tools is dedicated to delivering results that are not only targeted but also actionable. The emphasis is on providing users with information that is relevant to their investigations and capable of guiding informed decision-making.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or create a pull request.

> **License**

This project is licensed under the [MIT License](LICENSE).


