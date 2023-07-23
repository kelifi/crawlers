from configuration.config import AldiwanConfig, SustainabilityReportsConfig, SustainabilityAccountingReportConfig
from source.schema.base import ScraperName
from source.scraping_scripts.aldiwan_scraper import AldiwanScraper
from source.scraping_scripts.sustainability_accounting_reports_scraper import SustainabilityAccountingReportScraper
from source.scraping_scripts.sustainability_reports_scraper import SustainabilityReportsScraper


class ScraperFactory:
    '''
    A factory that selects and initializes the requested factory.

    When registring a new scraper:
        1 - add an entry in ScraperName enum
        2 - write a class that follows the abstract class WebScraper and a config class if necessary
        3 - maps the enum with the tuple (Scraper class, Scraper config) that you have created, voilà!
    '''

    def __init__(self):
        self.factory = {
            ScraperName.sustain: (SustainabilityReportsScraper, SustainabilityReportsConfig()),
            ScraperName.aldiwan: (AldiwanScraper, AldiwanConfig()),
            ScraperName.sustain_accounting: (SustainabilityAccountingReportScraper, SustainabilityAccountingReportConfig())
        }

    def __call__(self, scraper_name: ScraperName, *args, **kwargs):
        if factory_output := self.factory.get(scraper_name):
            scraper_class, scraper_config = factory_output
            return scraper_class(scraper_config=scraper_config, *args, **kwargs)
        else:
            raise ValueError('Invalid Scraper Name!')
