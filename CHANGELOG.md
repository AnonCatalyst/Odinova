# Scavenger OSINT GUI Update

## Changes Made:

---
**Bug Fix:** Freezing and Closing Issues

Additional error handling and debugging statements have been added to identify and address freezing and closing issues. If the tool freezes or closes unexpectedly, check the console for error messages and warnings.
---

### 1. Suppressing Deprecation Warnings:
- Added a warning filter to suppress `sipPyTypeDict` deprecation warnings.
- Redirected standard error to `/dev/null` (on Unix-like systems) to suppress libpng warnings.

### 2. Maigret Search Functionality Enhancement:
- Created a `MaigretSearchThread` class to run the Maigret OSINT tool in a separate thread.
- Introduced a `MaigretSearchGUI` class for the Maigret search user interface.
- Added a timer (`maigret_timer`) to notify the user in the logs tab every 15 seconds that Maigret is still running.
- Modified the `run_maigret_search` method to start and stop the Maigret timer.

### 3. Logging and User Feedback:
- Configured a logging module to log Maigret process start, end, and duration.
- Displayed a warning message when the user tries to search without entering a target username.
- Updated the Maigret results tab to show a message indicating that the search is ongoing.

### 4. Cleanup and Organization:
- Removed the `os.system("clear")` line as it might not work in all environments.
- Organized the code and imports for better readability.

### 5. Added Maigret Window to Side Menu:

- A new button named "Maigret" has been added to the side menu. Clicking on this button opens a new window for Maigret functionality.

### 6. Maigret Window Structure:

- The Maigret window contains an input box for the username and a result box to display the results. Users can input a username, hit the search button, and the tool will run a command using `os.system`:

### 7. Username Search Functionality:

- The username search functionality has been refactored to improve its efficiency and make the code more modular. The following changes were implemented:

    Threading for Parallel Requests:
        The threading mechanism has been revised to use Python's threading module for parallel requests. This change allows for faster username searches across multiple URLs simultaneously.

    Refactored Username Search Function:
        The username_search function has been refactored to use the requests library for making HTTP requests. The response handling has been improved to accurately identify valid usernames on web pages.

### 8. User Interface Enhancements:

- The user interface has been refined to provide a more intuitive and visually appealing experience. Notable changes include:

    Introduction of PyQt5:
        PyQt5 has been introduced to create a graphical user interface (GUI) for Scavenger. This change facilitates a more user-friendly interaction with the tool.

    Separated GUI Components:
        Different components of the tool, such as web search, Serpapi search, and user search, have been separated into individual GUI modules. This separation enhances code organization and maintainability.

### 9. Serpapi Integration:

- Integration with Serpapi, a search engine results API, has been added. Users can now perform searches using Serpapi by providing their API key. The following changes were made:

    Serpapi Search Module:
        A new module (SerpapiSearchGUI) has been introduced for Serpapi searches. Users can input their API key and search query to retrieve search results.

    API Key Saving Functionality:
        Users can now save their Serpapi API key for future use. The key is stored in a JSON file (serpapi_api_key.json).

### 10. Code Organization:

To enhance readability and maintainability, the codebase has been organized into distinct modules.

