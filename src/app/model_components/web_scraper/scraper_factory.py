from enum import Enum
from typing import Type

from .browsers_scraper import BrowserScraper
from .base import BaseScraper
from .dto import ScraperType




class ScraperFactory:
    """Factory for creating document readers"""
    
    _scrapers = {
        ScraperType.BROWER: BrowserScraper,

    }
    
    @classmethod
    def get_scraper(cls, scraper_type: ScraperType.BROWER) -> Type[BaseScraper]:
        scraper_class = cls._scrapers.get(scraper_type)
        if not scraper_class:
            raise ValueError(f"Unsupported scraper type: {scraper_type}")
        return scraper_class