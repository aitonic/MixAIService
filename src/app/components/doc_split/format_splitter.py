
import re
from typing import Any

from .base import DocSplitBase
from .dto import SplitParameter, SplitResult, SplitStrategy


class FormatSplitter(DocSplitBase):
    """Format-based document splitter that splits text based on formatting rules."""
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess the input text.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text

        """
        # Normalize line endings and ensure text starts and ends with newline
        text = text.replace('\r\n', '\n')
        return f"\n{text.strip()}\n"

    def _create_split_pattern(self, separator: str = None) -> str:
        """Create regex pattern for splitting text.
        
        Args:
            separator: Optional additional separator
            
        Returns:
            Regex pattern string

        """
        # Define common markdown separators
        patterns = [
            r'\n#{1,6}\s[^\n]*\n',  # Headers
            r'\n\*\*\*\n',          # Horizontal rules
            r'\n---\n',             # Alternative horizontal rules
            r'\n\n+',               # Multiple newlines (paragraphs)
        ]
        
        if separator:
            patterns.append(re.escape(separator))
            
        return '|'.join(patterns)

    def _split_by_format(self, text: str, pattern: str) -> list[str]:
        """Split text by formatting patterns.
        
        Args:
            text: Text to split
            pattern: Regex pattern for splitting
            
        Returns:
            List of text segments

        """
        # First split by headers
        header_pattern = r'\n(#{1,6}\s[^\n]*\n)'
        segments = []
        current_segment = ""
        
        # Split text into chunks by headers first
        for chunk in re.split(header_pattern, text):
            if chunk:  # Handle None or empty strings
                if chunk.strip().startswith('#'):
                    # If we have accumulated content, add it
                    if current_segment.strip():
                        segments.append(current_segment.strip())
                    current_segment = chunk
                else:
                    # Split non-header content by paragraphs
                    paragraphs = [p for p in chunk.split('\n\n') if p.strip()]
                    if current_segment:
                        # Add first paragraph to current segment if exists
                        if paragraphs:
                            current_segment += '\n' + paragraphs[0]
                            segments.append(current_segment.strip())
                            paragraphs = paragraphs[1:]
                        else:
                            segments.append(current_segment.strip())
                    # Add remaining paragraphs
                    segments.extend([p.strip() for p in paragraphs if p.strip()])
                    current_segment = ""
        
        # Add any remaining content
        if current_segment.strip():
            segments.append(current_segment.strip())
            
        return [seg for seg in segments if seg]  # Remove any empty segments

    def split(self, parameter: SplitParameter) -> SplitResult:
        """Split text based on formatting rules.
        
        Args:
            parameter: SplitParameter containing the text and configuration
            
        Returns:
            SplitResult containing the split segments

        """
        text = self._preprocess_text(parameter.text)
        pattern = self._create_split_pattern(parameter.separator)
        
        # Get initial segments
        segments = self._split_by_format(text, pattern)
        
        # Apply length constraints
        final_segments = []
        current_segment = ""
        
        for segment in segments:
            # If adding this segment would exceed max_length
            if len(current_segment) + len(segment) + 1 <= parameter.max_length:
                current_segment += (" " + segment if current_segment else segment)
            else:
                # Add current segment if it meets minimum length
                if current_segment and len(current_segment) >= parameter.min_length:
                    final_segments.append(current_segment.strip())
                # Start new segment
                current_segment = segment
        
        # Add last segment if it meets minimum length
        if current_segment and len(current_segment) >= parameter.min_length:
            final_segments.append(current_segment.strip())
        
        # Ensure we have at least one segment even if it's shorter than min_length
        if not final_segments and segments:
            final_segments = [segments[0].strip()]
        
        # Create metadata
        metadata = {
            "total_segments": len(final_segments),
            "format": "markdown" if any(s.startswith('#') for s in segments) else "plain",
            "has_headers": any(s.strip().startswith('#') for s in segments)
        }
        
        return SplitResult(
            chunks=final_segments,
            metadata=metadata,
            strategy=SplitStrategy.FORMAT
        )

    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> list[str]:
        """Split the input text using default or overridden parameters.

        Args:
            *args (tuple[Dict[str, Any], ...]): Arguments containing input parameters as a dictionary.
            **kwds (Dict[str, Any]): Additional keyword arguments.

        Returns:
            List[str]: Split segments.

        """
        param = args[0]  # Expecting a dictionary as the first argument
        params = {
            "text": param["text"],
            "strategy": SplitStrategy.FORMAT,
            "min_length": param.get("min_length", 50),
            "max_length": param.get("max_length", 1000),
            "model_name": param.get("model_name")
        }
        
        result = self.split(SplitParameter(**params))
        return result.chunks
