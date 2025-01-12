from dataclasses import dataclass
from enum import Enum

# from .constants import DEFAULT_EMBEDDING_MODEL

class SplitStrategy(Enum):
    """Enumeration of available splitting strategies."""

    FORMAT = "format"
    SEMANTIC = "semantic"

@dataclass
class SplitParameter:
    """Parameters for document splitting operations."""

    text: str
    strategy: SplitStrategy = SplitStrategy.FORMAT
    min_length: int = 50
    max_length: int = 1000
    overlap: int = 0
    separator: str | None = None
    model_name: str | None = None  # For semantic splitting

@dataclass
class SplitResult:
    """Results from document splitting operation."""

    segments: list[str]
    metadata: dict
    strategy: SplitStrategy
    
# @dataclass
# class EmbedParameter:
#     """Parameters for embedding operations."""
#     query: str
#     model: str = DEFAULT_EMBEDDING_MODEL
#     encoding_format: str = "float"
