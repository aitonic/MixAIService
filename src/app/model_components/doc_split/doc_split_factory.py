# app/model_components/doc_split/factory.py

from enum import Enum

from .format_splitter import FormatSplitter
from .semantic_splitter import SemanticSplitterWithEmbedding
from ..base_component import (
    BaseFactory,
    BaseComponent
)


class SplitterType(Enum):
    """Enumeration of available splitter types."""

    FORMAT = "format"
    SEMANTIC = "semantic"

class DocSplitterFactory(BaseFactory):
    """Factory class for creating document splitters."""
    
    def get_bean(self, param:dict) -> BaseComponent:
        """Create a document splitter instance.
        
        Args:
            splitter_type: Type of splitter to create
            embedding_model: Optional embedding model for semantic splitting
            **kwargs: Additional configuration parameters
            
        Returns:
            DocSplitBase: An instance of the requested splitter
            
        Raises:
            ValueError: If splitter_type is not recognized

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
