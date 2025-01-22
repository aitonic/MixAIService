"""Module: Scraper Factory

Purpose:
This module provides a factory class for creating scraper instances. Scrapers are 
used to fetch and process data from web pages or other sources. The factory pattern 
allows for easily extending the available scraper types and dynamically selecting 
the appropriate scraper implementation based on the input.

Main Features:
- `ScraperFactory`: A class for managing and creating scraper instances.
- Dynamic mapping of scraper types to their respective implementations.
- Supports adding new scraper types without modifying existing logic.

Dependencies:
- `BaseScraper`: Abstract base class for scrapers.
- `BrowserScraper`: Implementation of a browser-based scraper.
- `ScraperType`: Enum or constants defining the available scraper types.

Usage:
Use the `ScraperFactory.get_scraper` method to retrieve a scraper class based on the 
desired scraper type.
"""

from .base import BaseScraper
from .browsers_scraper import BrowserScraper
from .dto import ScraperType


class ScraperFactory:
    """Factory class for creating scrapers.

    This class manages the registration and retrieval of different scraper 
    implementations. It maps scraper types to their respective scraper classes.
    """

    # Mapping of scraper types to scraper implementations
    _scrapers = {
        ScraperType.BROWSER: BrowserScraper,
    }

    @classmethod
    def get_scraper(cls, scraper_type: ScraperType = ScraperType.BROWSER) -> type[BaseScraper]:
        """Retrieve the scraper class for the given scraper type.

        Args:
            scraper_type (ScraperType): The type of scraper to retrieve.

        Returns:
            type[BaseScraper]: The scraper class associated with the given scraper type.

        Raises:
            ValueError: If the provided scraper type is not supported.

        Example:
            ```python
            scraper_class = ScraperFactory.get_scraper(ScraperType.BROWSER)
            scraper_instance = scraper_class()
            ```

        """
        # Get the scraper class from the mapping
        scraper_class = cls._scrapers.get(scraper_type)
        if not scraper_class:
            # Raise an error if the scraper type is not supported
            raise ValueError(f"Unsupported scraper type: {scraper_type}")
        return scraper_class
