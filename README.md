# Async Web Scraper for MotionElements

## Overview

This project is an asynchronous web scraper designed to fetch and process data from specific web pages using proxy servers or without proxy server. It includes functionalities to test proxies, scrape data from a given range of pages, process the scraped data, and save the results to a database or csv file.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Python 3.8 or higher
- `asyncio`
- `pandas`
- `python-dotenv`
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/peterkacmarik/Async-Web-Scraper-MotionElements.git
    cd Async-Web-Scraper-MotionElements
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the root directory of the project and add the following environment variables:
    ```env
    DATABASE_URL_SQLITE = 'sqlite:///async-web-scraper-motionelements/database/sqlite.db'
    DATABASE_TABLE_SQLITE = 'motion_elements'

    LOG_DIR_MAIN = 'async-web-scraper-motionelements/logs/main_app.log'
    LOG_DIR_SCRAPING = 'async-web-scraper-motionelements/logs/scraper_app.log'
    LOG_DIR_FETCHING = 'async-web-scraper-motionelements/logs/fetcher_app.log'
    LOG_DIR_PROXIES = 'async-web-scraper-motionelements/logs/proxy_app.log'
    LOG_DIR_DATABASE = 'async-web-scraper-motionelements/logs/db_app.log'

    SETTINGS_APK = 'async-web-scraper-motionelements/settings/config_file.json'
    ```

2. Update the `config.py` file with the appropriate settings for your proxy and scraping configurations.

## Usage

To start the web scraping process, run the following command:
```sh
python app.py
```

### Example

```python
if __name__ == "__main__":
    app = RunApp()  # Create an instance of the RunApp class
    asyncio.run(app.startup())  # Run the startup coroutine
```

## Project Structure

```
async-web-scraper-motionelements/
│
├── database/
│   ├── models.py          # Database models and management
│   └── ...
│
├── logs/
│   ├── logger.py          # Logger configuration
│   └── ...
│
├── scraper/
│   ├── response_scraper.py # Handles fetching responses from pages
│   ├── data_scraper.py     # Handles data extraction and processing
│   └── ...
│
├── .env                   # Environment variables
├── config.py              # Configuration settings
├── app.py                 # Main script to run the application
├── proxy.py               # Proxy settings
├── requirements.txt       # Project dependencies
└── README.md              # Project README file
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.
This project is for educational purposes only. Always respect the terms of use of the websites you are scraping.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This README provides a basic overview of the project, including setup and usage instructions. As you add more code and features, we can update the relevant sections, such as configuration details, additional usage examples, and a more detailed project structure.
