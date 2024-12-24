# 分词策略
from .segmentation_strategy import SegmentationStrategy

# 上下文类，使用分词策略来分词
class SegmentationContext:
    """
    Context class that uses a segmentation strategy to segment text.
    """
    def __init__(self, strategy: SegmentationStrategy):
        """
        Initializes the context with a segmentation strategy.

        Args:
            strategy: The segmentation strategy to use.
        """
        self._strategy = strategy

    def set_strategy(self, strategy: SegmentationStrategy):
        """
        Sets the segmentation strategy.

        Args:
            strategy: The new segmentation strategy to use.
        """
        self._strategy = strategy

    def segment_text(self, text: str) -> list[str]:
        """
        Segments the given text using the current strategy.

        Args:
            text: The input text to segment.

        Returns:
            A list of segmented strings.
        """
        return self._strategy.segment(text)