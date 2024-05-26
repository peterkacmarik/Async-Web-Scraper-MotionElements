from typing import List, Dict
import os
import logging
from datetime import datetime
import asyncio
import pandas as pd
from dotenv import load_dotenv
from logs import logger
from scraper import ResponseScraper, DataScraper
from proxy import test_proxies
from config import _load_settings
from database.models import DatabaseManagerSettings, MotionsElements
from scraper.data_scraper import CheckNewItems


# Load environment variables
load_dotenv()

# Load logger settings from .env file
LOG_DIR_MAIN = os.getenv('LOG_DIR_MAIN')

# Create logger object
logger = logger.get_logger(log_file=LOG_DIR_MAIN, log_level=logging.INFO)


class RunApp:
    def __init__(self) -> None:
        """
        Initializes a new instance of the class.

        Returns:
            None

        Initializes the instance variables `start_page`, `end_page`, `category_id`, `response_scraper`,
        `num_test_proxies`, `working_proxies`, and `use_proxy` with the given values.
        """
        self.start_page: int = 3
        self.end_page: int = 4
        self.category_id: int = 38
        self.response_scraper: ResponseScraper = ResponseScraper(self.start_page, self.end_page, self.category_id)
        self.num_test_proxies: int = 50
        self.working_proxies: List = []
        self.use_proxy: bool = _load_settings()["proxy_settings"]["use_proxy"]

    async def startup(self) -> None:
        """
        Asynchronously starts up the application by performing a series of tasks related to scraping data from a website.
        
        This function is responsible for executing a series of tasks related to scraping data from a website. It performs the following steps:
        
        1. Measures the total time of the scraping process.
        2. Tests proxy servers before scraping, if the `use_proxy` flag is set to True.
        3. Fetches all pages with available proxies or without proxies.
        4. Raises a `RuntimeError` if no JSON data is found.
        5. Retrieves the URLs from the JSON response data.
        6. Raises a `RuntimeError` if no URLs are found.
        7. Measures the time taken to scrape the pages.
        8. Checks for new items and compares them with the database.
        9. Prints the DataFrame or raises a `RuntimeError` if no DataFrame is found.
        10. Saves the DataFrame to a CSV file or database.
        
        Parameters:
            self (RunApp): The instance of the RunApp class.
        
        Returns:
            None
        
        Raises:
            RuntimeError: If no working proxies are found, if no JSON data is found, if no URLs are found, or if no DataFrame is found.
            Exception: If an unhandled exception occurs during the scraping process.
        """
        try:
            # Total time of measurement of scraping
            total_start_time: datetime = datetime.now()

            # Test proxy servers before scraping
            if self.use_proxy == True:
                print(f'\t*** Start testing proxies... ***')
                start_time_test_proxy: datetime = datetime.now()
                self.working_proxies: List = await test_proxies(self.num_test_proxies)
                end_time_test_proxy: datetime = datetime.now()
                logger.info(f"*** Total time to test proxies: {end_time_test_proxy - start_time_test_proxy} ***\n")

                if not self.working_proxies:
                    raise RuntimeError("No working proxies found.")

            # Fetch all pages with available proxies or without proxies
            print(f'\t*** Start fetching category ID: {self.category_id}, pages from {self.start_page} to {self.end_page}... ***')
            start_time_fetch: datetime = datetime.now()
            json_data: List = await self.response_scraper._fetch_all_pages(self.working_proxies)
            end_time_fetch: datetime = datetime.now()
            logger.info(f"*** Total time to fetch: {end_time_fetch - start_time_fetch} ***\n")

            # If no JSON data is found, raise an error
            if not json_data:
                raise RuntimeError("No JSON data found.")

            # Get the URLs from the JSON response data
            print(f'\t*** Start scraping category ID: {self.category_id}, from page {self.start_page} to {self.end_page}... ***')
            start_time_scrape: datetime = datetime.now()
            list_urls: Dict = DataScraper()._get_url(json_data)
            end_time_scrape: datetime = datetime.now()
            logger.info(f"*** Total time to scrape: {end_time_scrape - start_time_scrape} ***\n")

            # If no URLs are found, raise an error
            if not list_urls['mp4_url'] and not list_urls['webm_url']:  # len(list_urls['mp4_url']) and len(list_urls['webm_url']) == 0:   # or not list_urls['mp4_url'] or not list_urls['webm_url']:
                raise RuntimeError("No parse data found.")

            # End of measurement of scraping
            total_end_time: datetime = datetime.now()
            logger.info(f"*** Total time to fetch and scrape pages: {total_end_time - total_start_time} ***\n")

            # Check new items
            print("\t*** Start checking new items... ***")
            start_time_check: datetime = datetime.now()
            df_to_insert = CheckNewItems().compare_details_with_db(list_urls)
            end_time_check: datetime = datetime.now()
            logger.info(f"*** Total time to check new items: {end_time_check - start_time_check} ***\n")

            # Print the DataFrame
            print("\t*** Start creating DataFrame... ***")
            df: pd.DataFrame = pd.DataFrame(df_to_insert)

            # Print the DataFrame or raise an error if no DataFrame is found
            if not df.empty:
                print(df)
            else:
                raise RuntimeError("*** No DataFrame found. ***")

            # Save DataFrame to CSV file
            # df.to_csv(f'async-web-scraper-motionelements/dataset/scraped_data_{self.start_page}-{self.end_page}.csv', index=False, encoding='utf-8-sig')
            # print("\t*** Data saved to CSV file... ***")

            # Save DataFrame to database
            DatabaseManagerSettings().insert_data(df, MotionsElements)
            DatabaseManagerSettings().close_connection()
            print("\t*** Data saved to database... ***")

        except Exception as e:
            # Handle unhandled exceptions
            logger.error("Error in run_main:", exc_info=True)


if __name__ == "__main__":
    app = RunApp()  # Create an instance of the RunApp class
    asyncio.run(app.startup())  # Run the startup coroutine
