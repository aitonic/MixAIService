import os
import re
from dataclasses import dataclass

from src.utils.logger import logger

from ..base_component import (
    BaseComponent, 
    BaseFactory
)
from .html_reader import HTMLDocReader
from .structured_reader import StructuredDocReader
from .unstructured_reader import UnstructuredDocReader


@dataclass
class HTMLReaderConfig:
    """Configuration for HTML reader."""

    llm_model: str
    max_tokens: int = 8192
    temperature: float = 0.7


class DocReaderFactory(BaseFactory):
    """Factory class to select the appropriate Reader based on file type or other logic."""

    def __init__(self) ->None:
        self._file_extension_map: dict[str, type[BaseComponent]] = {
            'csv': StructuredDocReader,
            'json': StructuredDocReader,
            'html': HTMLDocReader
        }
        self._default_reader = UnstructuredDocReader

    @staticmethod
    def is_web_url(url: str) -> bool:
        """Check if the given string is a valid web URL.

        Args:
            url (str): The string to be validated as a URL.

        Returns:
            bool: True if the input string matches a common URL pattern, False otherwise.

        """
        pattern = re.compile(
            r'^(https?:\/\/)?'  # Matches http:// or https://
            r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # Matches domain names
            r'(\/[^\s]*)?$'  # Matches optional path
        )
        return bool(pattern.match(url))

    def check(self, param: dict) -> None:
        """Override the check method.

        Args:
            param (dict): Input parameters for the factory.

        """
        logger.info(
            "Overridden check method, reader_factory does not require component_type validation."
        )

    def _create_html_reader(self, param: dict) -> HTMLDocReader:
        """Create an HTMLDocReader instance with the given parameters.

        Args:
            param (dict): Configuration parameters.

        Returns:
            HTMLDocReader: Configured HTML reader instance.

        """
        config = HTMLReaderConfig(
            llm_model=param["llm_model"],
            max_tokens=int(param.get("max_tokens", 8192)),
            temperature=float(param.get("temperature", 0.7))
        )
        return HTMLDocReader(
            llm_model=config.llm_model,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

    def _get_reader_for_file(self, file_path: str, param: dict) -> BaseComponent:
        """Get appropriate reader for a file based on its extension.

        Args:
            file_path (str): Path to the file.
            param (dict): Configuration parameters.

        Returns:
            BaseComponent: Appropriate document reader instance.

        """
        extension = file_path.split('.')[-1].lower()
        reader_class = self._file_extension_map.get(extension, self._default_reader)
        
        if reader_class is HTMLDocReader:
            return self._create_html_reader(param)
        return reader_class()

    def get_bean(self, param: dict) -> BaseComponent:
        """Get the appropriate document reader based on the input data type.

        Args:
            param (dict): Input parameters containing the key "query".

        Returns:
            BaseComponent: An appropriate document reader instance.

        Raises:
            ValueError: If the query data type is not supported.

        """
        source = param.get("query")

        # Handle web URLs
        if self.is_web_url(source):
            return self._create_html_reader(param)

        # Handle file paths
        if isinstance(source, str) and os.path.isfile(source):
            return self._get_reader_for_file(source, param)

        # Handle structured data
        if isinstance(source, dict | list):
            return StructuredDocReader()

        # Handle plain text
        if isinstance(source, str):
            return UnstructuredDocReader()

        raise ValueError("Unsupported data source type.")
