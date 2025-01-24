"""Document Splitter Factory Module.

This module provides a factory for creating different types of document splitters.
It uses a registry pattern to dynamically map splitter types to their implementations,
making it easy to add new splitter types without modifying existing code.

Typical usage example:
    factory = DocSplitterFactory()
    splitter = factory.get_bean({"component_type": "format"})
"""

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
    
    # Registry mapping splitter types to their implementation classes
    _splitter_registry: dict[str, type[BaseComponent]] = {
        SplitterType.FORMAT.value: FormatSplitter,
        SplitterType.SEMANTIC.value: SemanticSplitterWithEmbedding,
    }

    def get_bean(self, param: dict) -> BaseComponent:
        """Create a document splitter instance.

        Args:
            param (dict): Input parameters for creating the splitter. 
                - component_type (str): Type of splitter to create.
                - embedding_model (Optional[EmbeddingModel]): Embedding model for semantic splitting.
                - similarity_threshold (float): Threshold for semantic similarity.

        Returns:
            BaseComponent: An instance of the requested document splitter.

        Raises:
            ValueError: If component_type is not registered.

        """
        splitter_type = param["component_type"]
        splitter_class = self._splitter_registry.get(splitter_type)
        
        if not splitter_class:
            raise ValueError(f"Unknown splitter type: {splitter_type}")
        
        """specific parameters for semantic splitter"""
        if splitter_type == SplitterType.SEMANTIC.value:
            return splitter_class(
                embedding_model=param["embedding_model"],
                similarity_threshold=param["similarity_threshold"]
            )
            
        return splitter_class()
