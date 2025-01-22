"""Module: Browser Scraper Data Transfer Objects

This module defines the data structures used in the browser scraper component.
It includes classes for configuration, metadata, content, and results.

Classes:
- ScraperType: Enum for different types of scrapers
- PageMetadata: Metadata about a scraped page
- PageContent: Content and metadata from a scraped page
- ScraperResult: Result of a scraping operation
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ScraperType(Enum):
    """Enum defining different types of scrapers"""

    BROWSER = "browers"

@dataclass
class PageMetadata:
    """Metadata about a scraped webpage
    
    Attributes:
        url: The URL of the page
        title: Page title
        description: Meta description
        keywords: Meta keywords
        language: Page language
        author: Page author
        published_date: When the page was published
        modified_date: When the page was last modified
        favicon: URL to the favicon
        canonical_url: Canonical URL if different from accessed URL

    """

    url: str
    title: str | None = None
    description: str | None = None
    keywords: str | None = None
    language: str | None = None
    author: str | None = None
    published_date: datetime | None = None
    modified_date: datetime | None = None
    favicon: str | None = None
    canonical_url: str | None = None

@dataclass
class PageContent:
    """Content and metadata from a scraped webpage
    
    Attributes:
        raw_html: Raw HTML content of the page
        text_content: Extracted text content
        metadata: Page metadata
        headers: HTTP response headers
        scripts: List of script URLs
        stylesheets: List of stylesheet URLs
        images: List of image URLs
        links: List of links found on the page

    """

    raw_html: str
    text_content: str
    metadata: PageMetadata
    headers: dict[str, str]
    scripts: list[str] | None = None
    stylesheets: list[str] | None = None
    images: list[str] | None = None
    links: list[str] | None = None

@dataclass
class ScraperResult:
    """Result of a scraping operation
    
    Attributes:
        success: Whether the scraping was successful
        content: The scraped content if successful
        error_message: Error message if unsuccessful
        processing_time: Time taken to scrape in seconds
        status_code: HTTP status code
        redirect_chain: List of redirects if any occurred
        cache_hit: Whether result was from cache

    """

    success: bool
    content: PageContent | None = None
    error_message: str | None = None
    processing_time: float = 0.0
    status_code: int | None = None
    redirect_chain: list[str] | None = None
    cache_hit: bool = False

@dataclass
class ScraperStats:
    """Statistics about scraping operations
    
    Attributes:
        total_requests: Total number of requests made
        successful_requests: Number of successful requests
        failed_requests: Number of failed requests
        total_time: Total processing time
        average_time: Average processing time per request
        bytes_downloaded: Total bytes downloaded
        start_time: When scraping started
        end_time: When scraping ended

    """

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    bytes_downloaded: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None

@dataclass
class ScrapeRequest:
    """Configuration for a scrape request
    
    Attributes:
        url: URL to scrape
        method: HTTP method to use
        headers: Custom headers to send
        cookies: Cookies to include
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        allow_redirects: Whether to follow redirects
        max_redirects: Maximum number of redirects to follow

    """

    url: str
    method: str = "GET"
    headers: dict[str, str] | None = None
    cookies: dict[str, str] | None = None
    timeout: int = 30
    verify_ssl: bool = True
    allow_redirects: bool = True
    max_redirects: int = 5
    proxy: dict[str, str] | None = None
    javascript_enabled: bool = True
    wait_for_selectors: list[str] | None = None
    wait_until: str = "networkidle"
