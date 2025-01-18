"""
Base Scraper Module

This module defines the base classes and configurations for web scrapers.
It provides the foundation for different scraper implementations.

Author: ai
Created: 2025-01-18 08:22:56
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from .dto import ScraperResult

from playwright.async_api import Browser, BrowserContext, Page

@dataclass
class ScraperConfig:
    """Configuration for web scrapers
    
    Attributes:
        name: Name of the scraper instance
        headless: Whether to run browser in headless mode
        timeout: Default timeout in milliseconds
        proxy: Proxy configuration
        user_agent: Custom user agent string
        created_at: When this configuration was created
        created_by: Who created this configuration
    """
    name: str
    headless: bool = True
    timeout: int = 30000
    proxy: Optional[Dict[str, str]] = None
    user_agent: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    created_by: str = "system"

class BaseScraper(ABC):
    """Base class for all scraper implementations
    
    This class defines the common interface and functionality that all
    scraper implementations must provide.
    """
    
    def __init__(self, config: ScraperConfig):
        """Initialize the base scraper
        
        Args:
            config: Configuration for the scraper
        """
        self.config = config
        self.initialized: bool = False
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the scraper
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def read(self, url: str) -> ScraperResult:
        """Read content from the specified URL
        
        Args:
            url: The URL to scrape
            
        Returns:
            ScraperResult containing the scraped content or error information
        """
        pass
    
    async def cleanup(self) -> None:
        """Cleanup resources used by the scraper"""
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