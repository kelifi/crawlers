from abc import ABC, abstractmethod

from configuration.config import ScraperConfig


class WebScraper(ABC):
    '''
    Implemented scrapers should respect this contract a.k.a this abstract class

        constructor __init__ should have a scraper_config, then can use other args, kwargs...
        callable method __call__ is used to invoke the default behavior of the scraper

    '''

    @abstractmethod
    def __init__(self, scraper_config: ScraperConfig, *args, **kwargs):
        pass

    @abstractmethod
    def __call__(self, saving_location_dir: str):
        pass
