# app/model_components/doc_split/factory.py

from enum import Enum
from typing import Any

from ..model.embedding import OpenAiStyleEmbeddings
from .base import DocSplitBase
from .format_splitter import FormatSplitter
from .semantic_splitter import SemanticSplitterWithEmbedding


class SplitterType(Enum):
    """Enumeration of available splitter types."""

    FORMAT = "format"
    SEMANTIC = "semantic"

class DocSplitterFactory:
    """Factory class for creating document splitters."""
    
    @staticmethod
    def create_splitter(
        splitter_type: SplitterType,
        embedding_model: OpenAiStyleEmbeddings | None = None,
        **kwargs: dict[str, Any]
    ) -> DocSplitBase:
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
        if splitter_type == SplitterType.FORMAT:
            return FormatSplitter(**kwargs)
        elif splitter_type == SplitterType.SEMANTIC:
            return SemanticSplitterWithEmbedding(
                embedding_model=embedding_model,
                **kwargs
            )
        else:
            raise ValueError(f"Unknown splitter type: {splitter_type}")
