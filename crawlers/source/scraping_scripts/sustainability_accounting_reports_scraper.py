import os
import pathlib
import re
from typing import List
from urllib import request

from bs4 import BeautifulSoup
from tqdm import tqdm

from configuration.config import SustainabilityAccountingReportConfig, sustainability_esg_reports_config
from source.scraping_scripts.abstract import WebScraper
from source.utils.commons import Link
from source.utils.commons import download_pdf


class SustainabilityAccountingReportScraper(WebScraper):
    def __init__(self, scraper_config: SustainabilityAccountingReportConfig()):
        self.scraper_config = scraper_config

    def scrape_page(self, link) -> BeautifulSoup:
        """
        Scrape a page and return its soup.

        Args:
            link: The URL of the page to scrape.

        Returns:
            The BeautifulSoup object representing the parsed HTML content of the page.
        """
        # main_page = requests.get(link)
        req = request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        with request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')

        return BeautifulSoup(html_content, 'html.parser')

    def get_all_companies_reports(self) -> List[str]:

        """
        Retrieves all the links to the ESG reports of companies from the main page.

        Returns:
            A list of links (URLs) to the ESG reports of companies.
        """
        soup = self.scrape_page(link=Link(self.scraper_config.link))

        # Extract all the links from the 'a' tags on the main page
        pdf_urls = [company_tag["href"] for company_tag in soup.find_all('a', href=True) if
                    re.search(r'\.pdf$', company_tag["href"])]

        # Remove duplicates and return the list of PDF URLs
        return list(set(pdf_urls))

    def __call__(self, saving_location_dir: str) -> None:
        """This is the main function of this class it does the following steps:

            - Get the links to the companies' ESG reports.
            - Create the main folder where to save the data using `saving_location_dir`.
            - Loop on each company's main page link and extract the soup.
            - From the soup, extract the company's name and possible links.
            - Iterate over the links and download each PDF file, saving it in the company's folder.
            - Repeat steps 4 and 5 for each

            Note that some links can redirect you to another page indicating the file was removed or give you a 404 not
            found, for that a 10 seconds timeout was set when awaiting the response of the request"""
        all_reports_links = self.get_all_companies_reports()
        data_folder_path = os.path.join(saving_location_dir, "ESG_reports")
        if not os.path.exists(data_folder_path):
            os.makedirs(data_folder_path)
        os.chdir(data_folder_path)
        for report_link in tqdm(all_reports_links):
            file_name = report_link.split('/')[-1]  # Extract the filename from the URL
            save_path = f"{saving_location_dir}/{file_name}"  # Construct the save path

            download_pdf(
                url=report_link,
                save_path=save_path)


if __name__ == "__main__":
    scraper = SustainabilityAccountingReportScraper(
        scraper_config=sustainability_esg_reports_config)  # 4005 possible links
    root_path = pathlib.Path(__file__).parent.parent
    saving_directory = str(root_path)
    scraper(saving_location_dir=saving_directory)
