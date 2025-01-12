"""Constants for document splitting operations."""

# Default configurations
DEFAULT_MIN_LENGTH = 50
DEFAULT_MAX_LENGTH = 1000
DEFAULT_OVERLAP = 0

# Regular expression patterns
SENTENCE_END_PATTERN = r'([.!?])\s+'
MARKDOWN_HEADER_PATTERN = r'\n#{1,6}\s'
MARKDOWN_HR_PATTERN = r'\n(?:\*\*\*|\-\-\-)\n'

# Embedding Model
DEFAULT_EMBEDDING_MODEL = "jina-embeddings-v3"
DEFAULT_SIMILARITY_THRESHOLD = 70
