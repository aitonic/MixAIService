from typing import Any

from src.app.model_components.model.embedding import (
    EmbedParameter,
    OpenAiStyleEmbeddings,
)

# from ..base_component import BaseComponent
from .base import DocSplitBase
from .constants import DEFAULT_EMBEDDING_MODEL, DEFAULT_SIMILARITY_THRESHOLD
from .dto import SplitParameter, SplitResult, SplitStrategy
from .format_splitter import FormatSplitter


class SemanticSplitterWithEmbedding(DocSplitBase):
    """A semantic document splitter that uses embeddings to perform intelligent text segmentation.
    
    This splitter uses embedding-based similarity to determine optimal split points,
    ensuring that semantically related content stays together.
    """

    def __init__(self, embedding_model: OpenAiStyleEmbeddings | None = None,
                 similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> None:
        """Initialize the semantic splitter with embedding capabilities.
        
        Args:
            embedding_model: An instance of OpenAiStyleEmbeddings for computing text embeddings
            similarity_threshold: Threshold for determining semantic similarity (default: 0.7)

        """
        super().__init__()
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self._punctuation_pattern = r'([.!?])\s+'
        self.format_splitter = FormatSplitter()  
                
    def _compute_embedding_similarity(self, text1: str, text2: str) -> float:
        """Compute the cosine similarity between two text segments using embeddings.
        
        Args:
            text1: First text segment
            text2: Second text segment
            
        Returns:
            float: Similarity score between 0 and 1

        """
        print("\nComputing similarity with real API...")
        print(f"Text 1: {text1[:50]}...")
        print(f"Text 2: {text2[:50]}...")
        
        if not self.embedding_model:
            print("Warning: No embedding model available")
            return 0.0
            
        try:
            print("Getting embeddings from API...")
            emb1 = self.embedding_model.create(EmbedParameter(
                query=text1,
                model=DEFAULT_EMBEDDING_MODEL
            ))
            print("First embedding completed")
            
            emb2 = self.embedding_model.create(EmbedParameter(
                query=text2,
                model=DEFAULT_EMBEDDING_MODEL
            ))
            print("Second embedding completed")
            
            # 计算相似度
            import numpy as np
            vec1 = np.array(emb1[0]['embedding'])
            vec2 = np.array(emb2[0]['embedding'])
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            print(f"Computed similarity: {similarity}")
            print(f"current: {text1} and self.next_seg: {text2}")
            print(f"similarity:{similarity}")
            return float(similarity)
            
        except Exception as e:
            print(f"Error computing similarity: {str(e)}")
            raise
        
    def _merge_similar_segments(self, segments: list[str], max_length: int) -> list[str]:
        """Merge segments that are semantically similar while respecting max length.
        
        Args:
            segments: List of text segments to potentially merge
            max_length: Maximum length allowed for merged segments
            
        Returns:
            List[str]: Merged segments

        """
        if not segments:
            return segments

        merged = []
        current = segments[0]

        for next_seg in segments[1:]:
            combined_length = len(current) + len(next_seg) + 1  # +1 for space
            
            print("\nConsidering merge:")
            print(f"Current segment ({len(current)} chars): {current[:50]}...")
            print(f"Next segment ({len(next_seg)} chars): {next_seg[:50]}...")
            print(f"Combined length would be: {combined_length}")
            print(f"Max length allowed: {max_length}")

            if combined_length <= max_length:
                similarity = self._compute_embedding_similarity(current, next_seg)
                print(f"Computed similarity: {similarity}")
                print(f"Threshold: {self.similarity_threshold}")

                if similarity >= self.similarity_threshold:
                    print("Merging segments due to high similarity")
                    current = f"{current}\n{next_seg}"
                    continue
                else:
                    print("Not merging due to low similarity")
            else:
                print("Not merging due to length constraint")

            merged.append(current)
            current = next_seg

        merged.append(current)
        return merged
    
    def split(self, parameter: SplitParameter) -> SplitResult:
        """Split text using semantic embeddings for intelligent segmentation.
        
        Args:
            parameter: SplitParameter containing the text and configuration
            
        Returns:
            SplitResult: Object containing the split segments and metadata

        """
        # 检查输入是否已经是分割好的列表
        if isinstance(parameter.text, list):
            initial_segments = parameter.text
        else:
            # 使用 FormatSplitter 进行初始分割
            format_result = self.format_splitter.split(parameter)
            initial_segments = format_result.segments

        # 使用 embedding 模型合并相似段落
        if self.embedding_model:
            final_segments = self._merge_similar_segments(
                initial_segments,
                parameter.max_length
            )
        else:
            final_segments = initial_segments

        # 过滤太短的段落
        final_segments = [
            seg for seg in final_segments 
            if len(seg) >= parameter.min_length
        ]

        metadata = {
            "total_segments": len(final_segments),
            "strategy": "semantic_embedding",
            "model_name": parameter.model_name if parameter.model_name else "default",
            "similarity_threshold": self.similarity_threshold
        }

        return SplitResult(
            segments=final_segments,
            metadata=metadata,
            strategy=SplitStrategy.SEMANTIC
        )

    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> list[str]:
        """Split the input text using default or overridden parameters.

        Args:
            *args (tuple[Dict[str, Any], ...]): Arguments containing input parameters as a dictionary.
            **kwds (Dict[str, Any]): Additional keyword arguments.

        Returns:
            List[str]: Split segments.

        """
        param = args[0]
        params = {
            "text": param["text"],
            "strategy": SplitStrategy.SEMANTIC,
            "min_length": param.get("min_length", 50),
            "max_length": param.get("max_length", 1000),
            "model_name": param.get("model_name")
        }
        
        result = self.split(SplitParameter(**params))
        return result.segments
