import os
import pathlib
from typing import List

from bs4 import BeautifulSoup
from tqdm import tqdm

from configuration.config import SustainabilityReportsConfig, sustainability_reports_config
from source.scraping_scripts.abstract import WebScraper
from source.utils.commons import scrape_page, has_year, download_pdf, Link


class SustainabilityReportsScraper(WebScraper):
    def __init__(self, scraper_config: SustainabilityReportsConfig):
        self.scraper_config = scraper_config

    def get_all_companies(self) -> List[Link]:
        """From the main page of annual reports extract all companies' main pages.
        these links are under the "a" tag where the text is called "all annual reports" """
        soup = scrape_page(link=Link(self.scraper_config.link))
        return [company_tag["href"] for company_tag in soup.find_all('a', href=True) if
                company_tag.text == "all annual reports"]

    @staticmethod
    def extract_links_per_company(company_soup: BeautifulSoup) -> List[Link]:
        """From a soup of a company's main page, find all articles where the tag is called article and the id tag starts
        with post2, we will only extract links that contain a year like string inside the text of the tag.
        Note that the year inside the article div and the one in the link sometimes mismatch."""
        possible_links = []
        for article in company_soup.find_all(
                lambda tag: tag.name == 'article' and tag.get('id', '').startswith('post2')):
            possible_links.extend([e["href"] for e in article.find_all('a') if
                                   has_year(e.text)])  # checking if e.text is in english using langdetect is unreliable
        return possible_links

    @staticmethod
    def create_folders_per_company(data_path, company_name: str) -> None:
        """From a company create a folder with its name under data_path if it doesn't exist"""
        company_path = os.path.join(data_path, company_name)
        if not os.path.exists(company_path):
            os.makedirs(company_path)

    def __call__(self, saving_location_dir: str) -> None:
        """This is the main function of this class it does the following steps:
            -1- get the links to the companies' annual reports pages
            -2- create the main folder where to save the data using data_folder_path
            -3- loop on each company's main page link an extract the soup
            -4- from the soup extract the company's name and possible links
            -5- iterate over the link and download each pdf file and save it in the company's folder
            -6- repeat the 4th and 5th step

            Note that some links can redirect you to another page indicating the file was removed or give you a 404 not
            found, for that a 10 seconds timeout was set when awaiting the response of the request"""
        all_companies_links = self.get_all_companies()
        data_folder_path = os.path.join(saving_location_dir, "environment_data")
        if not os.path.exists(data_folder_path):
            os.makedirs(data_folder_path)
        os.chdir(data_folder_path)
        for company_link in tqdm(all_companies_links):
            company_soup = scrape_page(link=company_link)
            company_name = company_soup.find("h1", {"class": "entry-title"}).text
            self.create_folders_per_company(data_path=data_folder_path, company_name=company_name)
            company_links = self.extract_links_per_company(company_soup=company_soup)
            for index, possible_pdf in enumerate(company_links):
                download_pdf(
                    url=possible_pdf,
                    save_path=os.path.join(
                        data_folder_path, company_name, f"{str(index)}.pdf"
                    ),
                )


if __name__ == "__main__":
    scraper = SustainabilityReportsScraper(
        scraper_config=sustainability_reports_config)  # 256 possible links
    root_path = pathlib.Path(__file__).parent.parent
    saving_directory = str(root_path)
    scraper(saving_location_dir=saving_directory)
