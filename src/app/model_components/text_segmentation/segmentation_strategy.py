from abc import ABC, abstractmethod


class SegmentationStrategy(ABC):
    """Abstract base class for text segmentation strategies."""

    @abstractmethod
    def segment(self, text: str) -> list[str]:
        """Segments the given text into a list of strings.

        Args:
            text: The input text to segment.

        Returns:
            A list of segmented strings.

        """
        pass
