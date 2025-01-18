"""
Browser Scraper Implementation Module

This module implements a browser-based web scraper using Playwright.
It provides functionality for initializing a browser session and scraping web pages.

Author: ai
Created: 2025-01-18 08:15:53
"""

import asyncio
from src.utils.logger import logger
from typing import Optional, Dict, List
from datetime import datetime
from urllib.parse import urljoin

from playwright.async_api import async_playwright

from .base import BaseScraper, ScraperConfig
from .dto import (
    ScraperResult,
    PageContent,
    PageMetadata,
    ScrapeRequest
)

# logger = logging.getLogger(__name__)

class BrowserScraper(BaseScraper):
    """Browser-based web scraper implementation using Playwright"""
    
    # async def initialize(self) -> bool:
    #     """Initialize the browser session"""
    #     if self.initialized:
    #         return True
            
    #     try:
    #         playwright = await async_playwright().start()
    #         self.browser = await playwright.chromium.launch(
    #             headless=self.config.headless
    #         )
    #         self.context = await self.browser.new_context(
    #             proxy=self.config.proxy,
    #             user_agent=self.config.user_agent
    #         )
    #         self.page = await self.context.new_page()
    #         self.initialized = True
    #         logger.info("Browser initialized successfully")
    #         return True
    #     except Exception as e:
    #         logger.error(f"Failed to initialize browser: {str(e)}")
    #         return False
    
    # Class constants
    DEFAULT_TIMEOUT = 30000  # 30 seconds
    DEFAULT_SELECTOR_TIMEOUT = 5000  # 5 seconds
    MAX_RETRIES = 3
    
        # Resource selectors
    SELECTORS = {
        'scripts': ('script', 'src'),
        'stylesheets': ('link[rel="stylesheet"]', 'href'),
        'images': ('img', 'src'),
        'links': ('a', 'href'),
        'favicon': ('link[rel="icon"], link[rel="shortcut icon"]', 'href'),
        'canonical': ('link[rel="canonical"]', 'href')
    }
    
    async def initialize(self) -> bool:
        """Initialize the browser session
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self.initialized:
            return True
            
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.config.headless
            )
            self.context = await self.browser.new_context(
                proxy=self.config.proxy,
                user_agent=self.config.user_agent
            )
            self.page = await self.context.new_page()
            self.initialized = True
            logger.info(f"Browser initialized successfully for {self.config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            return False
    
    async def read(self, url: str, request_config: Optional[ScrapeRequest] = None) -> ScraperResult:
        """
        Scrape content from the specified URL
        
        Args:
            url: The URL to scrape
            request_config: Optional configuration for this specific request
            
        Returns:
            ScraperResult containing the scraped content or error information
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Configure request
            config = request_config or ScrapeRequest(url=url)
            
            # Navigate to page
            response = await self.page.goto(
                url,
                timeout=config.timeout * 1000,  # Convert to milliseconds
                wait_until=config.wait_until
            )
            
            if config.wait_for_selectors:
                for selector in config.wait_for_selectors:
                    try:
                        await self.page.wait_for_selector(selector, timeout=5000)
                    except Exception as e:
                        logger.warning(f"Failed to wait for selector {selector}: {str(e)}")
            
            # Extract metadata
            metadata = await self._extract_metadata(url)
            
            # Extract content
            content = await self._extract_content(metadata)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # 获取重定向链
            redirects = []
            if response:
                # 使用 response.url 获取最终URL
                final_url = response.url
                if final_url != url:
                    redirects = [url, final_url]  # 简单记录开始和结束URL
            
            return ScraperResult(
                success=True,
                content=content,
                processing_time=processing_time,
                status_code=response.status if response else None,
                redirect_chain=redirects
            )
            
        except Exception as e:
            error_msg = f"Failed to scrape {url}: {str(e)}"
            logger.error(error_msg)
            return ScraperResult(
                success=False,
                error_message=error_msg,
                processing_time=asyncio.get_event_loop().time() - start_time
            )
    
    async def _with_retry(self, operation, *args, max_retries=MAX_RETRIES):
        """Execute an operation with retry logic
        
        Args:
            operation: Async function to execute
            args: Arguments for the operation
            max_retries: Maximum number of retry attempts
            
        Returns:
            Result of the operation
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                return await operation(*args)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 指数退避
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                    await asyncio.sleep(wait_time)
                    
        logger.error(f"Operation failed after {max_retries} attempts: {str(last_error)}")
        raise last_error
    
    async def _extract_metadata(self, url: str) -> PageMetadata:
        """Extract metadata from the current page"""
        try:
            # Get basic metadata
            title = await self.page.title()
            
            # Extract meta tags
            meta_data = await self.page.evaluate('''() => {
                const meta = {};
                document.querySelectorAll('meta').forEach(m => {
                    const name = m.getAttribute('name') || m.getAttribute('property');
                    const content = m.getAttribute('content');
                    if (name && content) meta[name] = content;
                });
                return meta;
            }''')
            
            # Extract dates if available
            published_date = await self._parse_date(meta_data.get('article:published_time'))
            modified_date = await self._parse_date(meta_data.get('article:modified_time'))
            
            return PageMetadata(
                url=url,
                title=title,
                description=meta_data.get('description'),
                keywords=meta_data.get('keywords'),
                language=meta_data.get('language') or await self.page.evaluate('document.documentElement.lang'),
                author=meta_data.get('author'),
                published_date=published_date,
                modified_date=modified_date,
                favicon=await self._get_favicon(),
                canonical_url=await self._get_canonical_url()
            )
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return PageMetadata(url=url)
    
    async def _extract_content(self, metadata: PageMetadata) -> PageContent:
        """Extract content from the current page"""
        try:
            raw_html = await self.page.content()
            text_content = await self.page.evaluate('document.body.innerText')
            
            # Get HTTP headers
            headers = await self._get_headers()
            
            # Extract resources using predefined selectors
            scripts = await self._get_resource_urls(*self.SELECTORS['scripts'])
            stylesheets = await self._get_resource_urls(*self.SELECTORS['stylesheets'])
            images = await self._get_resource_urls(*self.SELECTORS['images'])
            links = await self._get_resource_urls(*self.SELECTORS['links'])
            
            return PageContent(
                raw_html=raw_html,
                text_content=text_content,
                metadata=metadata,
                headers=headers,
                scripts=scripts,
                stylesheets=stylesheets,
                images=images,
                links=links
            )
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            return PageContent(
                raw_html="",
                text_content="",
                metadata=metadata,
                headers={}
            )
    
    async def _get_resource_urls(self, selector: str, attr: str) -> List[str]:
        return await self._with_retry(self._get_resource_urls_internal, selector, attr)

    async def _get_resource_urls_internal(self, selector: str, attr: str) -> List[str]:
        """Extract resource URLs from the page using query_selector_all
        
        Args:
            selector: CSS selector to find elements
            attr: Attribute name containing the URL
            
        Returns:
            List of absolute URLs
        """
        try:
            elements = await self.page.query_selector_all(selector)
            urls = []
            for element in elements:
                url = await element.get_attribute(attr)
                if url:
                    urls.append(url)
            
            # Make URLs absolute
            base_url = self.page.url
            return [urljoin(base_url, url) for url in urls if url]
        except Exception as e:
            logger.error(f"Error extracting resources ({selector}): {str(e)}")
            return []
    
    async def _get_favicon(self) -> Optional[str]:
        """Extract favicon URL"""
        try:
            favicon = await self.page.evaluate('''() => {
                const link = document.querySelector('link[rel="icon"]') || 
                            document.querySelector('link[rel="shortcut icon"]');
                return link ? link.href : null;
            }''')
            return favicon
        except Exception:
            return None
    
    async def _get_canonical_url(self) -> Optional[str]:
        """Extract canonical URL"""
        try:
            canonical = await self.page.evaluate('''() => {
                const link = document.querySelector('link[rel="canonical"]');
                return link ? link.href : null;
            }''')
            return canonical
        except Exception:
            return None
    
    async def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            return None
        
    async def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers from the page"""
        try:
            return await self.page.evaluate('''() => {
                return Object.fromEntries(
                    performance.getEntriesByType('navigation')
                    .flatMap(entry => entry.serverTiming || [])
                    .map(timing => [timing.name, timing.description])
                );
            }''')
        except Exception as e:
            logger.error(f"Error getting headers: {str(e)}")
            return {}