import os

from src.utils.logger import logger

from ..base_component import BaseComponent, BaseFactory
from .structured_reader import StructuredDocReader
from .unstructured_reader import UnstructuredDocReader


class DocReaderFactory(BaseFactory):
    """Factory class to automatically select the appropriate Readerbased on file type or other logic."""

    def check(self, param: dict) -> None:
        """Override the `check` method. This factory does not require
        
        `component_type` validation and can use the `query` directly.

        Args:
            param (dict): Input parameters for the factory.

        """
        logger.info("Overridden check method, reader_factory does not require component_type validation.")

    def get_bean(self, param: dict) -> BaseComponent:
        """Get the appropriate document reader based on the input data type.

        Args:
            param (dict): Input parameters containing the key "query".

        Returns:
            BaseComponent: An instance of either `StructuredDocReader` or `UnstructuredDocReader`.

        Raises:
            ValueError: If the `query` data type is not supported.

        Example:
            ```python
            factory = DocReaderFactory()
            reader = factory.get_bean({"query": "example.csv"})
            ```

        """
        source = param.get("query")
        if isinstance(source, str) and os.path.isfile(source):
            # Determine reader type based on file extension
            if source.endswith(".csv") or source.endswith(".json"):
                return StructuredDocReader()
            else:
                # Default to unstructured for other file types
                return UnstructuredDocReader()
        else:
            # Handle plain text, URLs, or structured data
            if isinstance(source, dict | list):  # Combine isinstance checks
                return StructuredDocReader()
            elif isinstance(source, str):
                return UnstructuredDocReader()
            else:
                raise ValueError("Unsupported data source type.")
