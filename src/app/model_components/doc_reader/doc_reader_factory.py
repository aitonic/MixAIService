import os
import re

from src.utils.logger import logger

from ..base_component import BaseComponent, BaseFactory
from .html_reader import HTMLDocReader
from .structured_reader import StructuredDocReader
from .unstructured_reader import UnstructuredDocReader


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


class DocReaderFactory(BaseFactory):
    """Factory class to automatically select the appropriate Reader based on file type or other logic.
    """

    def check(self, param: dict) -> None:
        """Override the `check` method. This factory does not require `component_type` validation and can use the `query` directly.

        Args:
            param (dict): Input parameters for the factory.

        """
        logger.info(
            "Overridden check method, reader_factory does not require component_type validation."
        )

    def get_bean(self, param: dict) -> BaseComponent:
        """Get the appropriate document reader based on the input data type.

        Args:
            param (dict): Input parameters containing the key "query".

        Returns:
            BaseComponent: An instance of either `StructuredDocReader`, 
                `UnstructuredDocReader`, or `HTMLDocReader`.

        Raises:
            ValueError: If the `query` data type is not supported.

        Example:
            ```python
            factory = DocReaderFactory()
            reader = factory.get_bean({"query": "example.csv"})
            ```

        """
        source = param.get("query")
        if is_web_url(source):
            # HTML reader for web URLs
            return HTMLDocReader(
                llm_model=param["llm_model"],
                max_tokens=int(param["max_tokens"]) if "max_tokens" in param else 8192,
                temperature=float(param["temperature"]) if "temperature" in param else 0.7,
            )

        elif isinstance(source, str) and os.path.isfile(source):
            # Determine reader type based on file extension
            if source.endswith(".csv") or source.endswith(".json"):
                return StructuredDocReader()
            elif source.endswith(".html"):
                # HTML reader for HTML files
                return HTMLDocReader(
                    llm_model=param["llm_model"],
                    max_tokens=int(param["max_tokens"]) if "max_tokens" in param else 8192,
                    temperature=float(param["temperature"]) if "temperature" in param else 0.95,
                )
            else:
                # Default to unstructured reader for other file types
                return UnstructuredDocReader()
        else:
            # Handle plain text, URLs, or structured data
            if isinstance(source, dict | list):  # Use `|` for type union
                return StructuredDocReader()
            elif isinstance(source, str):
                return UnstructuredDocReader()
            else:
                raise ValueError("Unsupported data source type.")
