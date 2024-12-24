import re
from .segmentation_strategy import SegmentationStrategy

class ChineseSegmentation(SegmentationStrategy):
    """
    Concrete strategy for segmenting Chinese text based on sentences and paragraphs.
    """
    def segment(self, text: str) -> list[str]:
        """
        Segments the given Chinese text into sentences and paragraphs.

        Args:
            text: The input Chinese text to segment.

        Returns:
            A list of segmented strings.
        """
        # Split by paragraph breaks first
        paragraphs = re.split(r'\n+', text)
        sentences = []
        for paragraph in paragraphs:
            # Split by common Chinese sentence ending punctuation
            sentences.extend(re.split(r'([。？！])', paragraph))
        # Filter out empty strings
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences