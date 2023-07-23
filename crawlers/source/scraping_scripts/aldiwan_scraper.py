import os
import pathlib
from typing import List

import requests
from bs4 import BeautifulSoup
from loguru import logger
from tqdm import tqdm

from configuration.config import AldiwanConfig
from source.scraping_scripts.abstract import WebScraper
from source.utils.commons import scrape_page, Link


class AldiwanScraper(WebScraper):
    """This class provides functions to scrape aldiwan.net website."""

    def __init__(self, scraper_config: AldiwanConfig):
        self.scraper_config = scraper_config

    @staticmethod
    def get_poets_links(link: str) -> List[str]:
        """From a link containing one or many poets, extract the poets' names"""
        page_with_poets = scrape_page(link=link)
        set_of_poets = set()
        for element in page_with_poets.find_all('a', href=True):
            # links to poets contain 'cat' at the start
            if element["href"].startswith("cat"):
                set_of_poets.add(element["href"])
        return list(set_of_poets)

    def scrape_a_poet(self, poet_name: str) -> List[str]:
        """from a poet's name, construct the link directing to the poet's page.
        For example: https://www.aldiwan.net/cat-abounawes
        The function also scrapes all available poem names"""
        link = self.scraper_config.link + poet_name
        main_page = requests.get(link)
        soup = BeautifulSoup(main_page.content, "html.parser")
        # these are the poems
        poems = set()
        for element in soup.find_all('a', {"class": "float-right"}, href=True):
            if element["href"].startswith("poem"):
                poems.add(element["href"])
        return list(poems)

    def scrape_a_poem(self, poem_name: str) -> List[str]:
        """From a poem's name scrape its verses that are contained in a h3 HTML tag, the link to a poem is
        for example: https://www.aldiwan.net/poem111764.html"""
        link = self.scraper_config.link + poem_name
        soup = scrape_page(link=Link(link))
        poem_content = soup.find("div", {"id": "poem_content"})
        return [verse.text for verse in poem_content.find_all('h3')]

    def __call__(self, saving_location_dir: str) -> None:
        """ the scrape method loops on all possible pages, per letter and per poet and for each found poem
        the scraper finds and saves each poem in a directory with the name of the poet. Each poem file has each verse
        in a newline"""
        data_folder_path = os.path.join(saving_location_dir, "aldiwan_data")
        if not os.path.exists(data_folder_path):
            os.makedirs(data_folder_path)
        for link in tqdm(self.scraper_config.links):
            poets_per_letter = self.get_poets_links(link)  # get list of poets for the current letter
            # get poem names for a a poet:
            os.chdir(data_folder_path)
            for poet in poets_per_letter:
                poet_dir = os.path.join(data_folder_path, poet)
                if not os.path.exists(poet_dir):
                    os.makedirs(poet_dir)
                list_of_poems = self.scrape_a_poet(poet)
                for poem_name in list_of_poems:
                    if verses_list := self.scrape_a_poem(poem_name):
                        full_poem = "\n".join(verses_list)
                        file_path = os.path.join(poet, f"{poem_name}.txt")
                        with open(file_path, 'w') as f:
                            f.write(full_poem)


if __name__ == "__main__":
    root_path = pathlib.Path(__file__).parent.parent
    saving_directory = str(root_path)
    aldiwan_scraper = AldiwanScraper(scraper_config=AldiwanConfig())
    logger.info("Start aldiwan scraper")
    try:
        aldiwan_scraper(saving_location_dir=saving_directory)
        logger.info("Scraping aldiwan was successful!")
    except Exception as error_message:
        logger.error(str(error_message))
