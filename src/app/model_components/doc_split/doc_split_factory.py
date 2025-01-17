# app/model_components/doc_split/factory.py

from enum import Enum

from ..base_component import BaseComponent, BaseFactory
from .format_splitter import FormatSplitter
from .semantic_splitter import SemanticSplitterWithEmbedding


class SplitterType(Enum):
    """Enumeration of available splitter types."""

    FORMAT = "format"
    SEMANTIC = "semantic"

class DocSplitterFactory(BaseFactory):
    """Factory class for creating document splitters."""
    
    def get_bean(self, param:dict) -> BaseComponent:
        """Create a document splitter instance.

        Args:
            param (dict): Input parameters for creating the splitter. 
                - component_type (str): Type of splitter to create, e.g., "FORMAT" or "SEMANTIC".
                - embedding_model (Optional[EmbeddingModel]): Embedding model for semantic splitting (only required for "SEMANTIC").
                - similarity_threshold (float): Threshold for semantic similarity (only required for "SEMANTIC").

        Returns:
            BaseComponent: An instance of the requested document splitter.

        Raises:
            ValueError: If `component_type` is not recognized.

        """
        splitter_type = param["component_type"]
        if splitter_type == SplitterType.FORMAT.value:
            return FormatSplitter()
        elif splitter_type == SplitterType.SEMANTIC.value:
            return SemanticSplitterWithEmbedding(
                embedding_model=param["embedding_model"],
                similarity_threshold = param["similarity_threshold"]
            )
        else:
            raise ValueError(f"Unknown splitter type: {splitter_type}")
