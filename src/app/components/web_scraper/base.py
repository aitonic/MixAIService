"""Base Scraper Module

Purpose:
This module defines the foundational components for implementing web scrapers. It includes:
- A `ScraperConfig` class for scraper configurations.
- A `BaseScraper` abstract class that defines the common interface for scrapers.
- Resource management methods for handling browser instances.

Features:
- Configurable scraper setup with support for proxy and user-agent settings.
- Abstract methods (`initialize` and `read`) for implementation by specific scrapers.
- Automatic resource cleanup.

Author: ai
Created: 2025-01-19 01:59:59
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from playwright.async_api import Browser, BrowserContext, Page

from ..base_component import BaseComponent
from .dto import ScraperResult

T = TypeVar('T', bound=ScraperResult)

@dataclass
class ScraperConfig:
    """Configuration for web scrapers.

    Attributes:
        name (str): Name of the scraper instance.
        headless (bool): Whether to run the browser in headless mode. Defaults to True.
        timeout (int): Default timeout in milliseconds. Defaults to 30000.
        proxy (Optional[dict[str, str]]): Proxy configuration for the scraper.
        user_agent (Optional[str]): Custom user-agent string for the scraper.
        created_at (datetime): Timestamp of when the configuration was created.
        created_by (str): Name of the entity who created this configuration.

    """

    name: str
    headless: bool = True
    timeout: int = 30000
    proxy: dict[str, str] | None = None
    user_agent: str | None = None
    created_at: datetime = datetime.now()
    created_by: str = "ai"

class BaseScraper(ABC, Generic[T], BaseComponent):
    """Base class for all scraper implementations.

    This abstract class defines the interface and common functionality 
    for web scrapers. All specific scraper implementations should inherit 
    from this class and provide their own logic for initialization and scraping.
    """

    def __init__(self, config: ScraperConfig) -> None:
        """Initialize the base scraper.

        Args:
            config (ScraperConfig): Configuration for the scraper.

        """
        self.config = config
        self.initialized: bool = False
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the scraper.

        This method must be implemented by subclasses to perform specific initialization logic.

        Returns:
            bool: True if initialization is successful, False otherwise.

        """
        pass

    @abstractmethod
    async def read(self, url: str) -> T:
        """Read content from the specified URL.

        Args:
            url (str): The URL to scrape.

        Returns:
            T: An instance of `ScraperResult` containing the scraped content or error information.

        This method must be implemented by subclasses to perform specific scraping logic.

        """
        pass

    async def cleanup(self) -> None:
        """Cleanup resources used by the scraper.

        This method ensures proper closure of browser, context, and page resources.
        It should be called after scraping is complete or when an error occurs.
        """
        try:
            if self.page:
                await self.page.close()
                self.page = None

            if self.context:
                await self.context.close()
                self.context = None

            if self.browser:
                await self.browser.close()
                self.browser = None

            self.initialized = False
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
    
    # async def __call__(self, url: str) -> T:
    async def __call__(self, param: dict) -> T:
        """Execute the scraping operation in sequence.

        This method ensures the scraper is initialized before scraping and cleans up resources afterward.

        Args:
            url (str): The URL to scrape.

        Returns:
            T: The scraping result.

        Raises:
            Exception: If initialization fails or an error occurs during scraping.

        """
        try:
            # Ensure initialization
            if not self.initialized:
                init_success = await self.initialize()
                if not init_success:
                    raise RuntimeError("Failed to initialize scraper")

            # Perform scraping
            result = await self.read(param["url"])
            return result

        except Exception as e:
            # Cleanup on error
            await self.cleanup()
            raise e
