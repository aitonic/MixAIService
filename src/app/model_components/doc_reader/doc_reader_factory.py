import os

from .structured_reader import StructuredDocReader
from .unstructured_reader import UnstructuredDocReader
from ..base_component import (
    BaseFactory, 
    BaseComponent
)
from src.utils.logger import logger



class DocReaderFactory(BaseFactory):
    """Factory class for automatically selecting appropriate Reader based on file type or other logic.
    """

    def check(self, param:dict) -> None:
        
        logger.info(f"rewrite check func，reader_factoryno need param: component_type")

        
    def get_bean(self, param:dict) -> BaseComponent:
        """Get appropriate document reader based on input data type.

        Args:
            source (Union[str, dict, list]): Data source, could be file path string, dict or list.

        Returns:
            Union[StructuredDocReader, UnstructuredDocReader]: Appropriate document reader instance.

        Raises:
            ValueError: If input `source` type is not supported.

        """

        source = param.get("query")
        if isinstance(source, str) and os.path.isfile(source):
            # Determine reader based on file extension
            if source.endswith(".csv") or source.endswith(".json"):
                return StructuredDocReader()
            else:
                # Treat other formats as unstructured data
                return UnstructuredDocReader()
        else:
            # Could be plain text, URL, or dict/list data
            # Perform more detailed determination
            if isinstance(source, dict | list):
                return StructuredDocReader()
            elif isinstance(source, str):
                return UnstructuredDocReader()
            else:
                raise ValueError("Unsupported data source type.")
