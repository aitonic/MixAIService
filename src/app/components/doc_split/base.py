from abc import ABC, abstractmethod

from ..base_component import BaseComponent
from .dto import SplitParameter, SplitResult


class DocSplitBase(BaseComponent, ABC):
    """Base class for document splitting components.
    
    This class defines the interface for document splitting operations. It supports both
    format-based and semantic-based splitting strategies.
    """
    
    def __init__(self) -> None:
        """Initialize the document splitter."""
        super().__init__()
        
    @abstractmethod
    def split(self, parameter: SplitParameter) -> SplitResult:
        """Split the input document into segments.
        
        Args:
            parameter: SplitParameter object containing the input text and configuration
            
        Returns:
            SplitResult: Object containing the split segments and metadata

        """
        pass
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess the input text before splitting.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text

        """
        # Remove extra whitespace and normalize line endings
        text = text.strip()
        text = text.replace('\r\n', '\n')
        return text
    
    def _postprocess_segments(self, segments: list[str]) -> list[str]:
        """Post-process the split segments.
        
        Args:
            segments: List of split text segments
            
        Returns:
            Processed segments

        """
        return [seg.strip() for seg in segments if seg.strip()]
