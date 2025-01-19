"""Browser Scraper Implementation Module

This module implements a browser-based web scraper using Playwright.
It provides functionality for initializing a browser session and scraping web pages.

Features:
- Supports metadata extraction (title, description, keywords, etc.).
- Extracts content, including text, resources (scripts, images, stylesheets), and headers.
- Implements retry logic for operations prone to failure.
- Handles dynamic content loading with configurable wait conditions.

Author: ai
Created: 2025-01-18 08:15:53
"""

import asyncio
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import async_playwright

from src.utils.logger import logger

from .base import BaseScraper
from .dto import PageContent, PageMetadata, ScrapeRequest, ScraperResult


class BrowserScraper(BaseScraper):
    """Browser-based web scraper implementation using Playwright."""

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
        """Initialize the browser session.

        Returns:
            bool: True if initialization was successful, False otherwise.

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

    async def read(self, url: str, request_config: ScrapeRequest | None = None) -> ScraperResult:
        """Scrape content from the specified URL.

        Args:
            url (str): The URL to scrape.
            request_config (ScrapeRequest, optional): Optional configuration for this specific request.

        Returns:
            ScraperResult: Contains the scraped content or error information.

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

            # Extract metadata and content
            metadata = await self._extract_metadata(url)
            content = await self._extract_content(metadata)

            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time

            # Handle redirect chains
            redirects = []
            if response:
                final_url = response.url
                if final_url != url:
                    redirects = [url, final_url]

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

    async def _with_retry(
        self,
        operation: callable,
        *args: tuple[Any, ...],
        max_retries: int = MAX_RETRIES
    ) -> None:
        """Execute an operation with retry logic.

        Args:
            operation (callable): Async function to execute.
            args (tuple[Any, ...]): Arguments for the operation.
            max_retries (int): Maximum number of retry attempts.

        Returns:
            Any: Result of the operation.

        Raises:
            Exception: If the operation fails after all retries.

        """
        last_error = None
        for attempt in range(max_retries):
            try:
                return await operation(*args)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                    await asyncio.sleep(wait_time)

        logger.error(f"Operation failed after {max_retries} attempts: {str(last_error)}")
        raise last_error
    
    async def _extract_metadata(self, url: str) -> PageMetadata:
        """Extract metadata from the current page.

        Args:
            url (str): The URL being scraped.

        Returns:
            PageMetadata: Metadata of the page.

        """
        try:
            title = await self.page.title()

            meta_data = await self.page.evaluate('''() => {
                const meta = {};
                document.querySelectorAll('meta').forEach(m => {
                    const name = m.getAttribute('name') || m.getAttribute('property');
                    const content = m.getAttribute('content');
                    if (name && content) meta[name] = content;
                });
                return meta;
            }''')

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
        """Extract content from the current page.

        Args:
            metadata (PageMetadata): Metadata of the page.

        Returns:
            PageContent: Content of the page.

        """
        try:
            raw_html = await self.page.content()
            text_content = await self.page.evaluate('document.body.innerText')
            headers = await self._get_headers()
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

    async def _get_resource_urls(self, selector: str, attr: str) -> list[str]:
        """Extract resource URLs using retry logic."""
        return await self._with_retry(self._get_resource_urls_internal, selector, attr)

    async def _get_resource_urls_internal(self, selector: str, attr: str) -> list[str]:
        """Extract resource URLs from the page using a selector and attribute.

        Args:
            selector (str): CSS selector for the elements.
            attr (str): Attribute containing the resource URL.

        Returns:
            list[str]: List of resource URLs.

        """
        try:
            elements = await self.page.query_selector_all(selector)
            base_url = self.page.url
            urls = [urljoin(base_url, await element.get_attribute(attr)) for element in elements if element]
            return [url for url in urls if url]
        except Exception as e:
            logger.error(f"Error extracting resources ({selector}): {str(e)}")
            return []

    async def _get_favicon(self) -> str | None:
        """Extract the favicon URL."""
        try:
            return await self.page.evaluate('''() => {
                const link = document.querySelector('link[rel="icon"]') || 
                            document.querySelector('link[rel="shortcut icon"]');
                return link ? link.href : null;
            }''')
        except Exception:
            return None

    async def _get_canonical_url(self) -> str | None:
        """Extract the canonical URL."""
        try:
            return await self.page.evaluate('''() => {
                const link = document.querySelector('link[rel="canonical"]');
                return link ? link.href : null;
            }''')
        except Exception:
            return None

    async def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse a date string into a datetime object."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            return None

    async def _get_headers(self) -> dict[str, str]:
        """Extract HTTP headers from the current page.

        Returns:
            dict[str, str]: Dictionary of headers extracted from the page.

        """
        try:
            return await self.page.evaluate('''() => {
                const headers = {};
                const metaElements = document.querySelectorAll('meta[http-equiv]');
                metaElements.forEach(meta => {
                    const key = meta.getAttribute('http-equiv');
                    const value = meta.getAttribute('content');
                    if (key && value) {
                        headers[key.toLowerCase()] = value;
                    }
                });
                return headers;
            }''')
        except Exception as e:
            logger.error(f"Error getting headers: {str(e)}")
            return {}
