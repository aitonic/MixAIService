import unittest
import asyncio
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from src.app.model_components.web_scraper.base import ScraperConfig
from src.app.model_components.web_scraper.dto import (
    ScraperResult,
    PageContent,
    PageMetadata,
    ScraperType
)
from src.app.model_components.web_scraper.scraper_factory import ScraperFactory

class TestBrowserScraper(unittest.TestCase):
    """Test cases for BrowserScraper functionality"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.config = ScraperConfig(
            name="test_scraper",
            headless=True,
            timeout=30000,
            # created_by="jo",
            # created_at=datetime(2025, 1, 18, 7, 49, 42)
        )
        self.test_url = "https://www.meditrusthealth.com"
        
    async def async_setUp(self):
        """Async setup for browser initialization"""
        print(ScraperType.BROWER)
        self.scraper_class = ScraperFactory.get_scraper(ScraperType.BROWER)
        self.scraper = self.scraper_class(self.config)
        initialized = await self.scraper.initialize()
        self.assertTrue(initialized, "Failed to initialize browser scraper")

    async def async_tearDown(self):
        """Cleanup after each test"""
        if hasattr(self, 'scraper'):
            await self.scraper.cleanup()

    def run_async_test(self, coro):
        """Helper method to run async tests"""
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_scraper_initialization(self):
        """Test if scraper can be properly initialized"""
        async def _test():
            await self.async_setUp()
            self.assertIsNotNone(self.scraper)
            self.assertTrue(self.scraper.initialized)
            await self.async_tearDown()
        
        self.run_async_test(_test())

    def test_page_scraping(self):
        """Test if scraper can successfully scrape a webpage"""
        async def _test():
            await self.async_setUp()
            
            # Perform the scraping
            result = await self.scraper.read(self.test_url)
            
            # Assert the result
            self.assertTrue(result.success)
            self.assertIsNotNone(result.content)
            self.assertIsInstance(result.content, PageContent)
            self.assertGreater(len(result.content.text_content), 0)
            self.assertEqual(result.content.metadata.url, self.test_url)
            
            print(result.content)
            
            await self.async_tearDown()
            
        self.run_async_test(_test())

    def test_scraping_error_handling(self):
        """Test scraper's error handling with invalid URL"""
        async def _test():
            await self.async_setUp()
            
            # Test with invalid URL
            invalid_url = "https://invalid-url-that-does-not-exist.com"
            result = await self.scraper.read(invalid_url)
            
            # Assert the error handling
            self.assertFalse(result.success)
            self.assertIsNotNone(result.error_message)
            self.assertIsNone(result.content)
            
            await self.async_tearDown()
            
        self.run_async_test(_test())

    def test_metadata_extraction(self):
        """Test if scraper correctly extracts page metadata"""
        async def _test():
            await self.async_setUp()
            
            result = await self.scraper.read(self.test_url)
            
            # Assert metadata extraction
            self.assertTrue(result.success)
            self.assertIsNotNone(result.content.metadata)
            self.assertIsInstance(result.content.metadata, PageMetadata)
            self.assertIsNotNone(result.content.metadata.title)
            self.assertEqual(result.content.metadata.url, self.test_url)
            
            await self.async_tearDown()
            
        self.run_async_test(_test())

    def test_performance_metrics(self):
        """Test if scraper records performance metrics"""
        async def _test():
            await self.async_setUp()
            
            result = await self.scraper.read(self.test_url)
            
            # Assert performance metrics
            self.assertGreater(result.processing_time, 0)
            self.assertLess(result.processing_time, self.config.timeout / 1000)  # Convert ms to s
            
            await self.async_tearDown()
            
        self.run_async_test(_test())

    @unittest.skip("Skip proxy test if not configured")
    def test_proxy_configuration(self):
        """Test scraper with proxy configuration"""
        async def _test():
            # Create new config with proxy
            proxy_config = ScraperConfig(
                name="proxy_test_scraper",
                headless=True,
                timeout=30000,
                proxy={
                    'server': 'http://proxy.example.com:8080',
                    'username': 'user',
                    'password': 'pass'
                }
            )
            
            scraper = self.scraper_class(proxy_config)
            initialized = await scraper.initialize()
            self.assertTrue(initialized)
            
            result = await scraper.read(self.test_url)
            self.assertTrue(result.success)
            
            await scraper.cleanup()
            
        self.run_async_test(_test())

if __name__ == '__main__':
    unittest.main()