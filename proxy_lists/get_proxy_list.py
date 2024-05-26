from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
import requests
from rich import print
from config import _load_settings
import pandas as pd


def get_proxy_list_from_freeproxy_world():
    proxy_list = {
        "ip": [],
    }
    for page in range(1, 10 + 1):
        url = f"https://www.freeproxy.world/?type=http&anonymity=4&country=&speed=&port=&page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        table: object = soup.find("table")
        rows: list = table.find_all("tr")

        for row in rows:
            if row.find("td", class_="show-ip-div") is None:
                continue
            cols_ip = row.find("td", class_="show-ip-div").text.strip()
            cols_port = row.find('a').get('href').split("=")[1]
            ip_port = cols_ip + ":" + cols_port
            proxy_list['ip'].append(ip_port)

        df = pd.DataFrame(proxy_list)
        # print(df)
        # df.to_csv('async-web-scraper-motionelements/proxy/free_proxy_list.csv', index=False, encoding='utf-8')



# Function to get proxy list from API and return list of proxies
def get_proxy_list_from_api():
    """
    Retrieves a list of proxies from the ProxyScrape API.

    This function sends a GET request to the ProxyScrape API to retrieve a list of free proxies.
    The API URL is constructed with the following parameters:
    - request: getproxies
    - skip: 0
    - proxy_format: protocolipport
    - format: json
    - limit: 7 (number of proxies to retrieve at once)

    The function includes a set of headers to mimic a browser request.

    Returns:
        list: A list of proxies in the format 'protocol://ip:port'.
            The protocol is either 'http' or 'https'.

    Raises:
        requests.exceptions.RequestException: If there is an error with the request.
    """
    url: str = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&skip=0&proxy_format=protocolipport&format=json&limit=7"  # limit=20 = 20 proxies at once

    headers: dict = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'sk-SK,sk;q=0.9,cs;q=0.8,en-US;q=0.7,en;q=0.6',
    'origin': 'https://proxyscrape.com',
    'priority': 'u=1, i',
    'referer': 'https://proxyscrape.com/',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    response: requests.models.Response = requests.request("GET", url, headers=headers)
    json_data: dict = response.json()
    start_point: list = json_data['proxies']

    list_proxies: list = []
    for point in start_point:
        # proxies: str = f'{point["ip"]}:{point["port"]}'
        if point['protocol'] == 'http':
            list_proxies.append(point['proxy'])
        elif point['protocol'] == 'https':
            list_proxies.append(point["proxy"])
    return list_proxies


# Function to check availability of proxies and return list of available proxies
def check_proxies(proxies: list):
    """
    Check the availability of a list of proxies and return a list of available proxies.

    Parameters:
    - proxies (list): A list of proxy addresses to check.

    Raises:
    - ValueError: If the proxy list is empty.
    - ValueError: If the proxy check URL is empty.

    Returns:
    - list: A list of available proxy addresses.

    Note:
    - This function makes use of the `requests` library to send HTTP requests.
    - The function logs any errors or information related to the proxy availability.
    - The function measures the total time taken to check all proxies.
    """
    if proxies is None:
        raise ValueError('Proxy list is empty')

    proxy_check_url: str = _load_settings()['proxy_settings']['proxy_check_url']
    if proxy_check_url is None:
        raise ValueError('Proxy check URL is empty')

    start_time = datetime.now()

    available_proxies = []
    print(f'\n\t*** Number proxies to check: {len(proxies)} ***')
    for index, proxy in enumerate(proxies, start=1):
        if proxy is None:
            raise ValueError('Proxy is null')
        try:
            response: requests.models.Response = requests.get(proxy_check_url, proxies={"http": proxy, "https": proxy}, timeout=3)
            if response is None:
                print(f'Proxy {index} :: {proxy}  --  Null Response')
            elif response.status_code == 200:
                print(f'Proxy {index} :: {proxy}  --  Available')
                available_proxies.append(proxy)
            else:
                print(f'Proxy {index} :: {proxy}  --  Not Available ({response.status_code})')
        except requests.exceptions.ConnectTimeout as e:
            print(f'Proxy {index} :: {proxy}  --  Connect Timeout')
        except requests.exceptions.ConnectionError as e:
            print(f'Proxy {index} :: {proxy}  --  Connection Error')
        except requests.exceptions.InvalidURL as e:
            print(f'Proxy {index} :: {proxy}  --  Invalid URL')
        # except requests.exceptions.ProxyError as e:
        #     print(f'Proxy {index} :: {proxy}  --  Proxy Error')
        # except requests.exceptions.SSLError as e:
        #     print(f'Proxy {index} :: {proxy}  --  SSL Error')
        except requests.exceptions.Timeout as e:
            print(f'Proxy {index} :: {proxy}  --  Timeout')
        except requests.exceptions.TooManyRedirects as e:
            print(f'Proxy {index} :: {proxy}  --  Too Many Redirects')
        except Exception as e:
            print(f'Proxy {index} :: {proxy}  --  Unhandled Exception: {e}')

    end_time = datetime.now()
    print(f'Total time to check all proxies: {end_time - start_time}')
    print(f'Total available proxies for scraping: {len(available_proxies)}\n')
    return available_proxies

if __name__ == "__main__":
    # Get proxy list from API
    list_proxy = get_proxy_list_from_api()
    
    # Check proxy list and return list of available proxies
    available_proxy = check_proxies(list_proxy)
    # print(available_proxy)
    
    # create DataFrame from list of available proxies
    df = pd.DataFrame(available_proxy, columns=['proxy'])
    df.to_csv('async-web-scraper-motionelements/proxy/free_proxy_list.csv', index=False, encoding='utf-8')

    # Alternative way to get proxy list
    # get_proxy_list_from_freeproxy_world()
