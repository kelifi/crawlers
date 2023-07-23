from pathlib import Path
from typing import Optional

from loguru import logger
from typer import Typer

from source.schema.base import ScraperName
from source.scraping_scripts.scraper_factories import ScraperFactory

app = Typer()


@app.command(name="scrape")
def scrape(scraper_name: ScraperName, save_path: Optional[str] = None) -> None:
    '''
    Selects a scraper by scraper_name and performs its default scraping behavior

    :param scraper_name: should respect the values in ScraperName enum
    :param save_path: an optional argument to change where the data is saved
    :return: None
    '''
    scraper = ScraperFactory()(scraper_name)

    save_path = save_path if save_path is not None else str(scraper.scraper_config.root_directory)

    save_path = Path(save_path).absolute()

    if not save_path.exists():
        raise NotADirectoryError('Invalid save_path!')

    logger.info(f'Saving to {save_path}')

    scraper(str(save_path))


@app.command(name="list")
def list_scrapers() -> None:
    '''
    List available scrapers, scrapers should be registred by adding an entry in ScraperName enum
    :return:
    '''
    for entry in ScraperName:
        print(entry)


if __name__ == "__main__":
    # example: python main.py scrape sustain --save-path ./data
    app()
