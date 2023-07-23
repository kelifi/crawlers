import logging
import re
from typing import NewType

import requests
from bs4 import BeautifulSoup
from requests import ReadTimeout, HTTPError, ConnectionError, RequestException
from requests.exceptions import ChunkedEncodingError

Link = NewType("Link", str)  # Created a custom type based on str to remove ambiguity


def scrape_page(link: Link) -> BeautifulSoup:
    """Scrape a page and return its soup :)"""
    main_page = requests.get(link)
    return BeautifulSoup(main_page.content, "html.parser")


def download_pdf(url: Link, save_path: str, timeout: int = 10):
    """Download a pdf file from an url link and saves it in save_path
    ! a request will be sent and after 10 seconds it will pass it"""
    try:
        response = requests.get(url, timeout=timeout)  # if no timeout is provided it gets stuck
        response.raise_for_status()  # Check for any errors
        with open(save_path, 'wb') as file:
            file.write(response.content)
        logging.info(f"Downloaded {url}!")
    except ReadTimeout:
        logging.error(f"{url} was skipped because of timeout!")
    except (ConnectionError, HTTPError, ChunkedEncodingError) as error:
        logging.error(f"{url} has the following error {str(error)}!")
    except RequestException as error:
        logging.error(f"{url} encountered an unexpected error: {str(error)}!")
        # Handle the unexpected error or perform necessary actions



def has_year(string) -> bool:
    """Check if a string has a year in it denoted by 4 successive digits"""
    pattern = r'\b\d{4}\b'  # Matches a sequence of 4 digits
    match = re.search(pattern, string)
    return match is not None
