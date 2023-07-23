from pathlib import Path

from pydantic import BaseSettings


class ScraperConfig(BaseSettings):
    link: str
    root_directory: Path = Path(__file__).parent.parent


class AldiwanConfig(ScraperConfig):
    link: str = "https://www.aldiwan.net/"

    @property
    def links(self):
        """For each letter in the arabic alphabet, a link containing all possible poets starting with that letter
        can be found in (for example) https://www.aldiwan.net/letter1 that is for the letter alf"""
        return [f"https://www.aldiwan.net/letter{i}" for i in range(1, 28)]


class SustainabilityReportsConfig(ScraperConfig):
    link: str = "https://www.sustainability-reports.com/annual-reports/"


class SustainabilityAccountingReportConfig(ScraperConfig):
    link: str = 'https://www.sasb.org/company-use/sasb-reporters/'


aldiwan_config = AldiwanConfig()
sustainability_reports_config = SustainabilityReportsConfig()
sustainability_esg_reports_config = SustainabilityAccountingReportConfig()
