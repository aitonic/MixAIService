"""HTML converter module for processing and cleaning HTML content.

This module provides a class for HTML content manipulation, including cleaning,
replacing SVG content and base64 encoded images. All methods follow PEP8 standards
and include proper documentation.
"""

import re
from typing import Optional


class HTMLConverter:
    """A class for processing and converting HTML content.

    This class provides methods to clean HTML content by removing unnecessary
    elements and replacing potentially problematic content.

    Attributes:
        _SCRIPT_PATTERN (str): Regular expression pattern for script tags
        _STYLE_PATTERN (str): Regular expression pattern for style tags
        _META_PATTERN (str): Regular expression pattern for meta tags
        _COMMENT_PATTERN (str): Regular expression pattern for HTML comments
        _LINK_PATTERN (str): Regular expression pattern for link tags
        _BASE64_IMG_PATTERN (str): Regular expression pattern for base64 encoded images
        _SVG_PATTERN (str): Regular expression pattern for SVG elements
    """

    _SCRIPT_PATTERN = r"<[ ]*script.*?\/[ ]*script[ ]*>"
    _STYLE_PATTERN = r"<[ ]*style.*?\/[ ]*style[ ]*>"
    _META_PATTERN = r"<[ ]*meta.*?>"
    _COMMENT_PATTERN = r"<[ ]*!--.*?--[ ]*>"
    _LINK_PATTERN = r"<[ ]*link.*?>"
    _BASE64_IMG_PATTERN = r'<img[^>]+src="data:image/[^;]+;base64,[^"]+"[^>]*>'
    _SVG_PATTERN = r"(<svg[^>]*>)(.*?)(<\/svg>)"

    @classmethod
    def clean_html(
        cls,
        html: str,
        clean_svg: bool = False,
        clean_base64: bool = False
    ) -> str:
        """Clean HTML content by removing unnecessary elements.

        Args:
            html: The HTML content to clean
            clean_svg: Whether to replace SVG content with placeholder text
            clean_base64: Whether to replace base64 encoded images

        Returns:
            str: The cleaned HTML content
        """
        if not isinstance(html, str):
            raise ValueError("Input HTML must be a string")

        # Remove script tags
        html = cls._remove_pattern(html, cls._SCRIPT_PATTERN)
        # Remove style tags
        html = cls._remove_pattern(html, cls._STYLE_PATTERN)
        # Remove meta tags
        html = cls._remove_pattern(html, cls._META_PATTERN)
        # Remove HTML comments
        html = cls._remove_pattern(html, cls._COMMENT_PATTERN)
        # Remove link tags
        html = cls._remove_pattern(html, cls._LINK_PATTERN)

        if clean_svg:
            html = cls.replace_svg(html)
        if clean_base64:
            html = cls.replace_base64_images(html)

        return html

    @classmethod
    def replace_svg(
        cls,
        html: str,
        new_content: str = "this is a placeholder"
    ) -> str:
        """Replace SVG content with placeholder text.

        Args:
            html: The HTML content containing SVG elements
            new_content: The placeholder text to replace SVG content with

        Returns:
            str: HTML content with SVG elements replaced
        """
        return re.sub(
            cls._SVG_PATTERN,
            lambda match: f"{match.group(1)}{new_content}{match.group(3)}",
            html,
            flags=re.DOTALL
        )

    @classmethod
    def replace_base64_images(
        cls,
        html: str,
        new_image_src: str = "#"
    ) -> str:
        """Replace base64 encoded images with a simple image tag.

        Args:
            html: The HTML content containing base64 encoded images
            new_image_src: The source URL to use for replaced images

        Returns:
            str: HTML content with base64 images replaced
        """
        return re.sub(
            cls._BASE64_IMG_PATTERN,
            f'<img src="{new_image_src}"/>',
            html
        )

    @staticmethod
    def _remove_pattern(html: str, pattern: str) -> str:
        """Remove content matching a specific pattern from HTML.

        Args:
            html: The HTML content to process
            pattern: The regular expression pattern to match

        Returns:
            str: HTML content with matched patterns removed
        """
        return re.sub(
            pattern,
            "",
            html,
            flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
        )