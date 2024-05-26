import numpy as np
from typing import List, Dict, Any
import os
import logging
from dotenv import load_dotenv
import pandas as pd
from logs import logger
from database.models import DatabaseManagerSettings, MotionsElements


# Load environment variables
load_dotenv()

# Load logger settings from .env file
LOG_DIR_SCRAPING = os.getenv('LOG_DIR_SCRAPING')

# Create logger object
logger = logger.get_logger(log_file=LOG_DIR_SCRAPING, log_level=logging.INFO)


class DataScraper:
    def __init__(self) -> None:
        """
        Initializes a new instance of the class.

        This method initializes the `list_urls` attribute as a dictionary with keys "mp4_url", "webm_url", "category_id", 
        "category_name", "price", "currency", and "name". Each key is associated with an empty list.

        Parameters:
            None

        Returns:
            None
        """
        self.list_urls: Dict = {
            "mp4_url": [],
            "webm_url": [],
            "category_id": [],
            "category_name": [], 
            "price": [],
            "currency": [],
            "name": [],
        }

    def _get_url(self, json_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts mp4 and webm urls, category ids, category names, prices, currencies, and names from the given JSON data.

        Args:
            json_data (List[Dict[str, Any]]): A list of dictionaries representing JSON data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the extracted mp4 and webm urls, category ids, 
            category names, prices, currencies, and names. Each dictionary has the following keys:
                - "mp4_url" (List[str]): A list of mp4 urls.
                - "webm_url" (List[str]): A list of webm urls.
                - "category_id" (List[int]): A list of category ids.
                - "category_name" (List[str]): A list of category names.
                - "price" (List[Union[int, float]]): A list of prices.
                - "currency" (List[str]): A list of currencies.
                - "name" (List[str]): A list of names.

        Note:
            If any of the required keys are not found in the JSON data, the corresponding list will be empty.
            NaN values are used to represent missing values in the lists.

        Example:
            >>> data_scraper = DataScraper()
            >>> json_data = [
            ...     {
            ...         "data": [
            ...             {
            ...                 "previews": {
            ...                     "mp4": {"url": "https://example.com/mp4.mp4"},
            ...                     "webm": {"url": "https://example.com/webm.webm"}
            ...                 },
            ...                 "categories": [{"id": 1, "name": "Category 1"}],
            ...                 "price": 10.99,
            ...                 "currency": "USD",
            ...                 "name": "Example"
            ...             }
            ...         ]
            ...     }
            ... ]
            >>> result = data_scraper._get_url(json_data)
            >>> print(result)
            {
                "mp4_url": ["https://example.com/mp4.mp4"],
                "webm_url": ["https://example.com/webm.webm"],
                "category_id": [1],
                "category_name": ["Category 1"],
                "price": [10.99],
                "currency": ["USD"],
                "name": ["Example"]
            }
        """
        # Loop through the JSON data and extract the mp4 and webm urls
        for data in json_data:
            start_point: List[Dict[str, Any]] = data.get('data')

            # If no data is found, break the loop and return an empty list
            if len(start_point) == 0 or not start_point:
                break

            # Append the mp4 and webm urls to the list if they exist
            for point in start_point:
                previews: Dict[str, Any] = point.get('previews')
                categories: List[Dict[str, Any]] = point.get('categories')

                mp4_url: str = previews.get('mp4', {}).get('url')
                self.list_urls["mp4_url"].append(mp4_url if mp4_url else np.nan)

                webm_url: str = previews.get('webm', {}).get('url')
                self.list_urls["webm_url"].append(webm_url if webm_url else np.nan)

                category_id: int = categories[0].get("id")
                self.list_urls["category_id"].append(category_id if category_id else np.nan)

                category_name: str = categories[0].get("name")
                self.list_urls["category_name"].append(category_name if category_name else np.nan)

                price = point.get('price')
                self.list_urls["price"].append(price if price else np.nan)

                currency = point.get('currency')
                self.list_urls["currency"].append(currency if currency else np.nan)

                name = point.get('name')
                self.list_urls["name"].append(name if name else np.nan)
                
        # Print the number of mp4 and webm urls found
        logger.info(f"Number of mp4 urls: {len(self.list_urls['mp4_url'])} and webm urls: {len(self.list_urls['webm_url'])}")

        # Return the list of mp4, webm urls, category ids, and category names
        return self.list_urls


class CheckNewItems:
    def __init__(self) -> None:
        """
        Initializes the CheckNewItems class.

        This method creates an instance of the DatabaseManagerSettings class and assigns it to the `db_manager_settings` attribute of the CheckNewItems class.

        Parameters:
            None

        Returns:
            None
        """
        self.db_manager_settings = DatabaseManagerSettings()

    def compare_details_with_db(self, list_urls) -> pd.DataFrame:
        """
        Compares a list of URLs with a database to find new details to insert.

        Args:
            list_urls (list or dict): A list or dictionary of URLs to compare with the database.

        Returns:
            pd.DataFrame: A dataframe containing the new details to insert into the database.

        Raises:
            ValueError: If the parameter `list_urls` is empty.
            TypeError: If the parameter `list_urls` is not a dictionary.
            Exception: If an unexpected error occurs during the comparison process.

        Note:
            - The function creates a dataframe from the `list_urls` parameter.
            - The function defines column names for a blank dataframe to store new details.
            - The function loops through each row in the dataframe and checks if the URL already exists in the database.
            - If a new URL is found, the corresponding row is added to the dataframe.
            - If the URL is already in the database, the function skips it.
            - The function closes the database connection.
            - The function returns the dataframe with new details.
        """
        print("\t*** Start comparing details with database ***")
        if not list_urls:
            logger.error("The parameter list_urls cannot be empty")
            # raise ValueError('The parameter cars_details cannot be empty')
        if not isinstance(list_urls, Dict):
            logger.error("The parameter list_urls must be a Dict")
            # raise TypeError('The parameter cars_details must be a list')

        # Create dataframe from list
        df: pd.DataFrame = pd.DataFrame(list_urls)

        # Define column names for the blank dataframe to store new details
        column_names: list = [
            "mp4_url",
            "webm_url",
            "category_id",
            "category_name",
            "price",
            "currency",
            "name",
        ]
        
        # Create blank dataframe to store new details
        df_to_insert: pd.DataFrame = pd.DataFrame(columns=column_names)

        try:
            # Loop through each row in the dataframe
            for index, row in df.iterrows():
                # Get URL from dataframe
                mp4_url: str = row["mp4_url"]
                
                # Check if URL already exists in the database
                df_database: pd.DataFrame = self.db_manager_settings.read_data(
                    model=MotionsElements, conditions=MotionsElements.mp4_url == mp4_url
                )
                
                # If the URL is not in the database, add it to the dataframe
                if mp4_url not in df_database["mp4_url"].values:
                    logger.info(f"New URL found: {mp4_url}")
                    
                    # If a new URL is found, return the corresponding row
                    row_to_insert: pd.DataFrame = pd.DataFrame(
                        [row.values], columns=column_names
                    )
                    
                    # Append the new row to the dataframe
                    df_to_insert: pd.DataFrame = pd.concat(
                        [df_to_insert, row_to_insert], ignore_index=True
                    )
                    
                # If the URL is already in the database, skip it
                if mp4_url in df_database["mp4_url"].values:
                    logger.info(
                        f"Skipping... URL already exists in the database: {mp4_url}"
                    )
                    continue
                
        # Handle any exceptions that occur during the loop
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise
        
        # Close the database connection
        self.db_manager_settings.close_connection()
        
        # Return the dataframe with new details
        return df_to_insert