"""
Test Module for Browser Scraper

This module contains test cases for the browser scraper functionality,
including direct callable instance tests.

Author: ai
Created: 2025-01-19 02:20:49
"""

import unittest
from datetime import datetime
from pathlib import Path

from src.app.model_components.web_scraper.base import ScraperConfig
from src.app.model_components.web_scraper.dto import (
    ScraperResult,
    PageContent,
    PageMetadata,
    ScraperType
)
from src.app.model_components.web_scraper.scraper_factory import ScraperFactory
from src.utils.logger import logger

class TestBrowserScraper(unittest.IsolatedAsyncioTestCase):
    """Test cases for BrowserScraper functionality"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.config = ScraperConfig(
            name="test_scraper",
            headless=True,
            timeout=30000,
            created_by="josangmi",
            created_at=datetime(2025, 1, 19, 2, 20, 49)
        )
        self.test_url = "https://www.meditrusthealth.com"
        # self.test_url = "https://www.sina.com.cn"

        self.scraper = None
        
        # Create test outputs directory
        self.output_dir = Path(__file__).parent / "test_outputs"
        self.output_dir.mkdir(exist_ok=True)

    async def asyncSetUp(self):
        """Async setup before each test method"""
        self.scraper = ScraperFactory.get_scraper(ScraperType.BROWER)(self.config)

    async def asyncTearDown(self):
        """Cleanup after each test"""
        if self.scraper:
            await self.scraper.cleanup()

    async def test_direct_call(self):
        """Test direct calling of scraper instance using __call__ method"""
        # Test single call
        result = await self.scraper(self.test_url)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.content)
        
        # Test multiple consecutive calls
        urls = [
            self.test_url,
            f"{self.test_url}/about",
            # f"{self.test_url}/contact"
        ]
        
        results = []
        for url in urls:
            try:
                result = await self.scraper(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
        
        # Verify results
        self.assertEqual(len(results), len(urls))
        for result in results:
            self.assertTrue(hasattr(result, 'success'))
            if result.success:
                self.assertIsNotNone(result.content)
                self.assertIsInstance(result.content, PageContent)
                self.assertIsInstance(result.content.metadata, PageMetadata)

    async def test_call_with_error_handling(self):
        """Test error handling when calling scraper instance directly"""
        # Test with invalid URL
        invalid_url = "https://invalid-url-that-does-not-exist.com"
        result = await self.scraper(invalid_url)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)

        # Test with empty URL
        with self.assertRaises(ValueError):
            await self.scraper("")

        # Test with None URL
        with self.assertRaises(ValueError):
            await self.scraper(None)

    async def test_call_with_large_page(self):
        """Test scraper performance with large page"""
        large_page_url = "https://www.meditrusthealth.com"  # Replace with actual large page URL
        
        # Record start time
        start_time = datetime.utcnow()
        
        # Perform scraping
        result = await self.scraper(large_page_url)
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Verify performance
        self.assertTrue(result.success)
        self.assertLess(duration, self.config.timeout / 1000)  # Convert ms to s
        
        # Save results
        if result.success:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"large_page_{timestamp}.html"
            output_file.write_text(result.content.raw_html, encoding='utf-8')
            
            # Log performance metrics
            logger.info(f"Large page scraping completed in {duration:.2f} seconds")
            logger.info(f"Content size: {len(result.content.raw_html)} bytes")
            logger.info(f"Output saved to: {output_file}")

    async def test_call_with_retry(self):
        """Test scraper's retry mechanism when calling directly"""
        # Create a list of URLs with one invalid URL in the middle
        urls = [
            self.test_url,
            "https://invalid-url-that-does-not-exist.com",
            # f"{self.test_url}/contact"
        ]
        
        results = []
        for url in urls:
            try:
                # Each call should handle its own retry logic
                result = await self.scraper(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to scrape {url} after retries: {str(e)}")
                results.append(None)
        
        # Verify results
        self.assertEqual(len(results), len(urls))
        # First and last URLs should succeed
        self.assertTrue(results[0].success if results[0] else False)
        # self.assertTrue(results[2].success if results[2] else False)
        # Middle URL should fail
        self.assertFalse(results[1].success if results[1] else True)

    async def test_call_save_results(self):
        """Test saving results when using direct call"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Perform scraping using direct call
            result = await self.scraper(self.test_url)
            
            if result.success:
                # Save HTML content
                html_file = self.output_dir / f"direct_call_{timestamp}.html"
                html_file.write_text(result.content.raw_html, encoding='utf-8')
                
                # Save metadata
                import json
                metadata_file = self.output_dir / f"direct_call_metadata_{timestamp}.json"
                metadata = {
                    "url": result.content.metadata.url,
                    "title": result.content.metadata.title,
                    "scrape_time": timestamp,
                    "processing_time": result.processing_time,
                    "success": result.success,
                    "status_code": result.status_code
                }
                metadata_file.write_text(
                    json.dumps(metadata, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                
                # Verify files
                self.assertTrue(html_file.exists())
                self.assertTrue(metadata_file.exists())
                
                # Log success
                logger.info(f"Successfully saved scraping results:")
                logger.info(f"HTML: {html_file}")
                logger.info(f"Metadata: {metadata_file}")
            else:
                self.fail(f"Scraping failed: {result.error_message}")
                
        except Exception as e:
            self.fail(f"Test failed with error: {str(e)}")

if __name__ == '__main__':
    unittest.main()