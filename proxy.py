import logging
import random
import asyncio
import os
import csv
from aiohttp_socks import ProxyError
from logs import logger
from dotenv import load_dotenv
from rich import print
from config import _load_settings
import aiohttp


# Load environment variables
load_dotenv()

# Load logger settings from .env file
LOG_DIR_PROXIES = os.getenv('LOG_DIR_PROXIES')

# Create logger object
logger = logger.get_logger(log_file=LOG_DIR_PROXIES, log_level=logging.INFO)


def _get_proxy(num_test_proxies: int):
    """
    Reads a list of proxies from a CSV file and returns a random sample of the specified number of proxies.

    Args:
        num_test_proxies (int): The number of proxies to be returned.

    Returns:
        list: A random sample of the specified number of proxies.

    Raises:
        FileNotFoundError: If the proxy list file does not exist.
        ValueError: If the proxy list is empty.
    """
    # Load proxy list from path in settings
    proxy_list_path: str = _load_settings()['proxy_settings']['proxy_list5']

    # Sync method to read one proxy list from file
    with open(proxy_list_path, 'r') as file:
        reader: csv.reader = csv.reader(file)   # Read proxy list from CSV file
        proxy_list: list = ['http://' + row[0] for row in reader]   # Prepend 'http://' to each row in the file
        return random.sample(proxy_list, k=num_test_proxies)    # Return a random sample of the specified number of proxies


async def _test_proxy(proxy: str, index: int, checker_url: list):
    """
    Asynchronously tests a proxy by sending a GET request to a randomly chosen URL from the provided checker_url list.
    
    :param proxy: The proxy to test.
    :type proxy: str
    :param index: The index of the proxy in the list.
    :type index: int
    :param checker_url: The list of URLs to choose from for testing the proxy.
    :type checker_url: list
    :return: The tested proxy if it is working, None otherwise.
    :rtype: str or None
    """
    # Delay between requests
    delay: int = 1

    # Generate random URL for proxy checking
    url = random.choice(checker_url) if checker_url else None
    
    # If proxy is None, raise ValueError
    if not url:
        logger.error("No URL provided for proxy checking.")
        return None
    
    # Create connector and timeout objects
    connector: aiohttp.BaseConnector = aiohttp.TCPConnector(ssl=False, limit=100)  # Turn off SSL verification for testing
    timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=30)
    
    try:
        # Create aiohttp session and send GET request
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            try:
                # Send GET request with proxy and random delay
                async with session.get(url=url, proxy=proxy) as response:
                    await asyncio.sleep(random.uniform(0.5, 5.0))   # Add random delay between requests

                    # Check response status
                    if response.status == 200:
                        logger.info(f"Proxy {index}: {proxy} WORKING")
                        return proxy

                    # Handle 429 and 504 errors
                    elif response.status == 429:
                        logger.warning(f"Proxy {index}: {proxy} too many requests")
                        await asyncio.sleep(60)  # Wait for 60 seconds before retrying
                        return await _test_proxy(proxy, index, checker_url)

                    elif response.status == 504:
                        logger.warning(f"Proxy {index}: {proxy} timed out")
                        return None
                    
                    # Handle other status codes
                    else:
                        logger.error(f"Proxy {index}: {proxy} failed with status {response.status} - URL: {url}")
                        return None
            
            # Handle proxy errors
            except ProxyError as e:
                logger.error(f"Error {e}, retrying in {delay} seconds...")
                await asyncio.sleep(delay)  # Add delay before retrying
                delay *= 2   # Double the delay
    
    # Handle other errors
    except Exception as e:
        # logger.error(f"Proxy {index}: {proxy} failed with exception: {e}")
        return None


async def _get_working_proxies(proxy_list: list, checker_url: list):
    """
    Asynchronously tests a list of proxies and returns a list of working proxies.

    Args:
        proxy_list (List[str]): A list of proxies to test.
        checker_url (List[str]): A list of URLs to check the proxies against.

    Returns:
        List[str]: A list of working proxies.

    Raises:
        None
    """
    # Test each proxy in parallel using asyncio gathering method
    tasks: list = [_test_proxy(proxy, index, checker_url) for index, proxy in enumerate(proxy_list)]

    # Wait for all tasks to complete
    working_proxies: list = await asyncio.gather(*tasks)

    # Remove None values from the list and return it
    return [proxy for proxy in working_proxies if proxy is not None]


async def test_proxies(num_test_proxies: int):
    """
    Asynchronously tests a list of proxies and returns a list of working proxies.

    Args:
        num_test_proxies (int): The number of proxies to test.

    Returns:
        List[str]: A list of working proxies.

    Raises:
        None

    This function loads a list of proxies from the settings and a list of URLs to check the proxies against. If no URL is provided, an empty list is returned. The function then tests the proxies in parallel using asyncio and returns a list of working proxies.
    """
    # Load proxy list from path in settings
    proxy_list: list = _get_proxy(num_test_proxies)
    
    # Load proxy checker URL from settings
    checker_url: list = _load_settings()["proxy_settings"]["checker_proxies"]
    
    # If no URL is provided, return an empty list
    if not checker_url:
        logger.error("No URL provided for proxy checking.")
        return []   # Return an empty list
    
    # Get working proxies in parallel using asyncio
    working_proxies: list = await _get_working_proxies(proxy_list, checker_url)
    return working_proxies  # Return the list of working proxies
