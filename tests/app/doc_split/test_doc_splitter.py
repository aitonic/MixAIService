"""
Test suite for document splitter factory and its products.

Created by: ai
Created at: 2025-01-11 14:26:17 UTC
"""

from typing import List, Dict, Any
import unittest
from unittest.mock import Mock, patch
import numpy as np

from src.app.model_components.doc_split.doc_split_factory import DocSplitterFactory, SplitterType
from src.app.model_components.doc_split.dto import SplitParameter, SplitStrategy, SplitResult
from src.app.model_components.model.dto import BaseLLMParameter, EmbedParameter
from src.app.model_components.doc_split.base import DocSplitBase
from src.app.model_components.doc_split.format_splitter import FormatSplitter
from src.app.model_components.doc_split.semantic_splitter import SemanticSplitterWithEmbedding
from src.app.model_components.model.embedding import OpenAiStyleEmbeddings


class TestDocSplitterFactory(unittest.TestCase):
    """Test cases for DocSplitterFactory and its products."""
    def setUp(self) -> None:
        """Set up test fixtures."""
        print("\nSetting up test case...")
        
        # Create mock embedding model for regular tests
        self.mock_embedding_model = Mock(spec=OpenAiStyleEmbeddings)
        self.mock_embedding_model.create = Mock()
        
        print(f"Mock embedding model created: {self.mock_embedding_model}")
        print(f"Mock has create method: {hasattr(self.mock_embedding_model, 'create')}")
        
        # Create real embedding model for API tests
        self.real_embedding_model = OpenAiStyleEmbeddings(
            parameter=BaseLLMParameter(
                api_key="test-key",
                base_url="http://192.168.11.11:8070",
                full_url="http://192.168.11.11:8070/v1/embeddings",
                max_retry=2
            )
        )
        
        # Create factory and splitters
        self.factory = DocSplitterFactory()
        self.format_splitter = self.factory.create_splitter(SplitterType.FORMAT)
        
        # Create both mock and real semantic splitters
        print("Creating semantic splitters...")
        self.mock_semantic_splitter = self.factory.create_splitter(
            SplitterType.SEMANTIC,
            embedding_model=self.mock_embedding_model
        )
        self.real_semantic_splitter = self.factory.create_splitter(
            SplitterType.SEMANTIC,
            embedding_model=self.real_embedding_model
        )
        
        # Sample texts for testing
        self.markdown_text = """
        # Section 1
        
        This is a paragraph about topic A.
        
        ## Subsection 1.1
        
        This is more detail about topic A.
        
        # Section 2
        
        This is a paragraph about topic B.
        """
        
        self.plain_text = """
        First sentence about AI technology.
        Second sentence about machine learning.
        Third sentence about deep neural networks.
        Fourth sentence about natural language processing.
        """

    def test_factory_creates_format_splitter(self) -> None:
        """Test factory creates FormatSplitter correctly."""
        splitter = self.factory.create_splitter(SplitterType.FORMAT)
        self.assertIsInstance(splitter, FormatSplitter)
        self.assertIsInstance(splitter, DocSplitBase)

    def test_factory_creates_semantic_splitter(self) -> None:
        """Test factory creates SemanticSplitterWithEmbedding correctly."""
        splitter = self.factory.create_splitter(
            SplitterType.SEMANTIC,
            embedding_model=self.real_embedding_model
        )
        self.assertIsInstance(splitter, SemanticSplitterWithEmbedding)
        self.assertIsInstance(splitter, DocSplitBase)

    def test_factory_invalid_type(self) -> None:
        """Test factory raises error for invalid splitter type."""
        with self.assertRaises(ValueError):
            self.factory.create_splitter("invalid_type")

    # def test_format_splitter_markdown(self) -> None:
    #     """Test FormatSplitter with markdown text."""
    #     splitter = self.factory.create_splitter(SplitterType.FORMAT)
        
    #     parameter = SplitParameter(
    #         text=self.markdown_text,
    #         strategy=SplitStrategy.FORMAT,
    #         min_length=10,
    #         max_length=200
    #     )
        
    #     result = splitter.split(parameter)
        
    #     self.assertIsInstance(result, SplitResult)
    #     self.assertGreater(len(result.segments), 1)
    #     # Check if sections are properly split
    #     self.assertTrue(
    #         any("Section 1" in segment for segment in result.segments)
    #     )
    #     self.assertTrue(
    #         any("Section 2" in segment for segment in result.segments)
    #     )

    # def test_format_splitter_plain_text(self) -> None:
    #     """Test FormatSplitter with plain text."""
    #     splitter = self.factory.create_splitter(SplitterType.FORMAT)
        
    #     parameter = SplitParameter(
    #         text=self.plain_text,
    #         strategy=SplitStrategy.FORMAT,
    #         min_length=10,
    #         max_length=100
    #     )
        
    #     result = splitter.split(parameter)
        
    #     self.assertIsInstance(result, SplitResult)
    #     self.assertGreater(len(result.segments), 1)
    #     # Check if paragraphs are properly split
    #     for segment in result.segments:
    #         self.assertLessEqual(len(segment), 100)

    def test_format_splitter_markdown(self) -> None:
        """Test FormatSplitter with markdown text."""
        
        splitter = self.factory.create_splitter(SplitterType.FORMAT)
        markdown_text = """# Header 1
                    This is the first paragraph.

                    ## Header 2
                    This is the second paragraph.

                    ### Header 3
                    This is the third paragraph."""

        parameter = SplitParameter(
            text=markdown_text,
            strategy=SplitStrategy.FORMAT,
            min_length=5,
            max_length=100
        )
        
        result = splitter.split(parameter)
        
        self.assertGreater(len(result.segments), 1)
        self.assertEqual(result.strategy, SplitStrategy.FORMAT)
        self.assertTrue(any('Header 1' in seg for seg in result.segments))
        self.assertTrue(any('Header 2' in seg for seg in result.segments))

    def test_format_splitter_plain_text(self) -> None:
        """Test FormatSplitter with plain text."""
        
        splitter = self.factory.create_splitter(SplitterType.FORMAT)

        plain_text = """First paragraph with some content.

                    Second paragraph with different content.

                    Third paragraph with more text."""

        parameter = SplitParameter(
            text=plain_text,
            strategy=SplitStrategy.FORMAT,
            min_length=5,
            max_length=100
        )
        
        result = splitter.split(parameter)
        
        self.assertGreater(len(result.segments), 1)
        self.assertEqual(result.strategy, SplitStrategy.FORMAT)
        self.assertTrue(any('First paragraph' in seg for seg in result.segments))
        self.assertTrue(any('Second paragraph' in seg for seg in result.segments))
        
    def test_semantic_splitter_text_similarity(self) -> None:
        """Test SemanticSplitter with text similarity."""
        splitter = self.factory.create_splitter(
            SplitterType.SEMANTIC,
            embedding_model=self.mock_embedding_model,
            similarity_threshold=0.7
        )
        
        # Text with similar topics
        similar_text = """
        First sentence about artificial intelligence.
        Second sentence about AI applications.
        Third sentence about AI implementation.
        """
        
        parameter = SplitParameter(
            text=similar_text,
            strategy=SplitStrategy.SEMANTIC,
            min_length=10,
            max_length=200
        )
        
        result = splitter.split(parameter)
        
        self.assertIsInstance(result, SplitResult)
        # Similar sentences should be merged
        self.assertLess(len(result.segments), 3)

    def test_semantic_splitter_different_topics(self) -> None:
        """Test SemanticSplitter with different topics using real API.
        
        Created by: ai
        Created at: 2025-01-12 13:24:41 UTC
        """
        print("\nStarting different topics test with real API...")
        
        # 使用 markdown 格式的测试文本，包含明确的主题分隔
        different_topics = """
        # Programming
        Programming is a fundamental skill in software development.
        Python is one of the most popular programming languages.
        It's widely used in AI and web development.

        # Cooking
        Cooking is both an art and a science.
        Baking bread requires precise measurements and timing.
        Understanding temperature control is crucial.

        # Gardening
        Gardening helps connect with nature.
        Growing vegetables requires patience and care.
        Different plants need different soil conditions.
        """
        
        parameter = SplitParameter(
            text=different_topics,
            strategy=SplitStrategy.SEMANTIC,
            min_length=10,
            max_length=200
        )
        
        print("\nAPI Configuration:")
        print(f"Base URL: {self.real_embedding_model.base_url}")
        print(f"Full URL: {self.real_embedding_model.embed_url}")
        print(f"API Key: {self.real_embedding_model.api_key[:5]}...")
        
        try:
            print("\nExecuting split operation with real API...")
            
            # 获取原始分割结果（使用 FormatSplitter）
            format_splitter = FormatSplitter()
            format_result = format_splitter.split(parameter)
            print("\nInitial format split result:")
            print(f"Number of format segments: {len(format_result.segments)}")
            for i, segment in enumerate(format_result.segments, 1):
                print(f"Format segment {i}: {segment[:100]}...")
            
            # 使用语义分割器进行处理
            semantic_splitter = self.factory.create_splitter(
                SplitterType.SEMANTIC,
                embedding_model=self.real_embedding_model,
                similarity_threshold=0.7
            )
            result = semantic_splitter.split(parameter)
            
            print(f"\nFinal semantic split result:")
            print(f"Number of segments: {len(result.segments)}")
            for i, segment in enumerate(result.segments, 1):
                print(f"Segment {i}: {segment[:100]}...")
            
            # 基本验证
            self.assertIsInstance(result, SplitResult)
            self.assertEqual(result.strategy, SplitStrategy.SEMANTIC)
            
            # 验证段落数量
            self.assertEqual(
                len(result.segments), 
                3, 
                f"Expected 3 segments but got {len(result.segments)}"
            )
            
            # 验证每个主题都存在
            topics = ["programming", "cooking", "gardening"]
            for topic in topics:
                self.assertTrue(
                    any(topic.lower() in seg.lower() for seg in result.segments),
                    f"Missing segment about {topic}"
                )
            
            # 验证段落长度限制
            for segment in result.segments:
                self.assertLessEqual(
                    len(segment), 
                    parameter.max_length,
                    "Segment exceeds maximum length"
                )
                self.assertGreaterEqual(
                    len(segment),
                    parameter.min_length,
                    "Segment is shorter than minimum length"
                )
            
            # 打印相似度矩阵
            print("\nSimilarity matrix:")
            n = len(result.segments)
            similarity_matrix = [[0.0] * n for _ in range(n)]
            
            for i in range(n):
                for j in range(i + 1, n):
                    similarity = semantic_splitter._compute_embedding_similarity(
                        result.segments[i],
                        result.segments[j]
                    )
                    similarity_matrix[i][j] = similarity_matrix[j][i] = similarity
                    print(f"Similarity between segment {i+1} and {j+1}: {similarity:.4f}")
            
            # 验证主题间的相似度
            for i in range(n):
                for j in range(i + 1, n):
                    self.assertLess(
                        similarity_matrix[i][j],
                        semantic_splitter.similarity_threshold,
                        f"Segments {i+1} and {j+1} are too similar"
                    )
            
            # 验证 metadata
            self.assertIn("similarity_threshold", result.metadata)
            self.assertEqual(result.metadata["total_segments"], len(result.segments))
            
        except Exception as e:
            print(f"\nError during test: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            raise

    @patch('httpx.Client')
    def test_semantic_splitter_mock_integration(self, mock_client):
        """Test semantic splitter with mocked API.
        
        Created by: ai
        Created at: 2025-01-12 13:12:47 UTC
        """
        print("\nStarting mock integration test...")
        
        # 设置 mock 响应
        emb_vector = [0.1] * 10
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "data": [
                {
                    "embedding": emb_vector,
                    "index": 0,
                    "object": "embedding"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        
        # 配置 mock client
        mock_client_instance = mock_client.return_value.__enter__.return_value
        mock_client_instance.post.return_value = mock_response

        # 准备 markdown 格式测试文本
        markdown_text = """
        # AI Technology
        First paragraph about AI technology and deep learning.
        More details about neural networks.

        ## Machine Learning
        Second paragraph about machine learning algorithms.
        Additional information about training models.
        """

        parameter = SplitParameter(
            text=markdown_text,
            strategy=SplitStrategy.SEMANTIC,
            min_length=10,
            max_length=100
        )

        def mock_create(param: EmbedParameter) -> List[Dict[str, Any]]:
            print(f"\nMocked embedding request for text: {param.query[:50]}...")
            return [{"embedding": emb_vector}]
        
        self.mock_embedding_model.create.side_effect = mock_create

        try:
            # 执行分割
            result = self.mock_semantic_splitter.split(parameter)

            # 验证 API 调用
            api_calls = mock_client_instance.post.call_args_list
            print(f"\nMock API calls: {len(api_calls)}")
            
            for i, call in enumerate(api_calls, 1):
                args, kwargs = call
                print(f"\nMock Call #{i}:")
                print(f"URL: {args[0] if args else kwargs.get('url', 'No URL')}")
                print(f"Headers: {kwargs.get('headers', {})}")
                print(f"Data: {kwargs.get('json', {})}")

            # 验证结果
            self.assertIsInstance(result, SplitResult)
            self.assertEqual(result.strategy, SplitStrategy.SEMANTIC)
            self.assertGreater(len(result.segments), 0)
            
            # 验证内容
            self.assertTrue(any("AI" in seg for seg in result.segments))
            self.assertTrue(any("machine learning" in seg for seg in result.segments))

        except Exception as e:
            print(f"\nError during test: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            raise

    def test_semantic_splitter_real_api(self):
        """Test semantic splitter with real API integration.
        
        Created by: ai
        Created at: 2025-01-12 13:12:47 UTC
        """
        print("\nStarting real API integration test...")

        # 预分割的段落列表
        segments = [
            "First paragraph about artificial intelligence and machine learning.",
            "Second paragraph about deep neural networks.",
            "Third paragraph about data science and analytics."
        ]

        parameter = SplitParameter(
            text=segments,  # 直接传入预分割的列表
            strategy=SplitStrategy.SEMANTIC,
            min_length=10,
            max_length=150
        )

        print("\nAPI Configuration:")
        print(f"Base URL: {self.real_embedding_model.base_url}")
        print(f"Full URL: {self.real_embedding_model.embed_url}")
        print(f"API Key: {self.real_embedding_model.api_key[:5]}...")

        try:
            print("\nExecuting split with real API...")
            result = self.real_semantic_splitter.split(parameter)
            
            print(f"\nSplit result:")
            print(f"Number of segments: {len(result.segments)}")
            for i, segment in enumerate(result.segments, 1):
                print(f"Segment {i}: {segment}")

            # 基本验证
            self.assertIsInstance(result, SplitResult)
            self.assertEqual(result.strategy, SplitStrategy.SEMANTIC)
            
            # 验证长度限制
            for segment in result.segments:
                self.assertLessEqual(len(segment), parameter.max_length)
            
            # 验证最小长度
            for segment in result.segments:
                self.assertGreaterEqual(len(segment), parameter.min_length)

        except Exception as e:
            print(f"\nError during real API call: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            raise

    def test_semantic_splitter_with_mock(self):
        """Test semantic splitter with mock embedding model using markdown text.
        
        Created by: ai
        Created at: 2025-01-12 13:40:12 UTC
        """
        print("\nStarting semantic splitter mock test with markdown...")
        
        # 1. 配置 mock embedding vectors
        mock_vectors = {
            "ai": np.array([1.0, 0.0, 0.0]),
            "cooking": np.array([0.0, 1.0, 0.0]),
            "gardening": np.array([0.0, 0.0, 1.0])
        }
        
        # 2. 配置 mock embedding 函数
        def mock_create(param: EmbedParameter) -> List[Dict[str, Any]]:
            text = param.query.lower()
            print(f"\nProcessing text for embedding: {text[:50]}...")
            
            # 根据文本内容返回对应向量
            if "ai" in text or "machine" in text:
                vector = mock_vectors["ai"]
            elif "cooking" in text or "baking" in text:
                vector = mock_vectors["cooking"]
            elif "gardening" in text or "plant" in text:
                vector = mock_vectors["gardening"]
            else:
                vector = np.array([0.33, 0.33, 0.33])
                
            print(f"Generated vector: {vector}")
            return [{"embedding": vector}]
        
        self.mock_embedding_model.create.side_effect = mock_create

        # 3. 准备 markdown 测试文本
        markdown_text = """
    # AI and Machine Learning

    Content about AI technology.
    More about machine learning algorithms.
    Deep learning applications.

    # Cooking and Baking

    Content about cooking recipes.
    More about baking techniques.
    Kitchen experiments.

    # Gardening and Plants

    Content about garden maintenance.
    More about growing plants.
    Seasonal planting tips.
    """

        # 4. 创建参数对象
        parameter = SplitParameter(
            text=markdown_text,
            strategy=SplitStrategy.SEMANTIC,
            min_length=5,
            max_length=200
        )

        try:
            # 5. 首先使用 FormatSplitter 进行初始分割
            print("\nExecuting format split...")
            format_splitter = FormatSplitter()
            format_result = format_splitter.split(parameter)
            
            print("\nFormat Split Result:")
            print(f"Number of format segments: {len(format_result.segments)}")
            for i, segment in enumerate(format_result.segments, 1):
                print(f"Format Segment {i}: {segment}")
                print("-" * 50)

            # 6. 创建语义分词器实例
            semantic_splitter = SemanticSplitterWithEmbedding(
                embedding_model=self.mock_embedding_model,
                similarity_threshold=0.5  # 使用较低的阈值确保段落不会被合并
            )
            
            # 7. 使用格式分割的结果进行语义分割
            print("\nExecuting semantic split...")
            parameter.text = format_result.segments  # 使用格式分割的结果
            result = semantic_splitter.split(parameter)
            
            print("\nSemantic Split Result:")
            print(f"Number of segments: {len(result.segments)}")
            for i, segment in enumerate(result.segments, 1):
                print(f"Semantic Segment {i}: {segment}")
                print("-" * 50)

            # 8. 计算段落间相似度
            print("\nComputing similarities between segments:")
            for i in range(len(result.segments)):
                for j in range(i+1, len(result.segments)):
                    similarity = semantic_splitter._compute_embedding_similarity(
                        result.segments[i],
                        result.segments[j]
                    )
                    print(f"Similarity between segments {i+1} and {j+1}: {similarity:.4f}")

            # 9. 验证结果
            self.assertEqual(
                len(result.segments),
                3,
                f"Expected 3 segments but got {len(result.segments)}"
            )
            
            # 10. 验证每个主题的存在性
            topics = {
                "AI": False,
                "cooking": False,
                "gardening": False
            }
            
            for segment in result.segments:
                segment_lower = segment.lower()
                if "ai" in segment_lower or "machine" in segment_lower:
                    topics["AI"] = True
                if "cooking" in segment_lower or "baking" in segment_lower:
                    topics["cooking"] = True
                if "gardening" in segment_lower or "plant" in segment_lower:
                    topics["gardening"] = True

            for topic, found in topics.items():
                self.assertTrue(
                    found,
                    f"Missing segment about {topic}\nSegments: {result.segments}"
                )

            # 11. 验证长度限制
            for i, segment in enumerate(result.segments, 1):
                self.assertLessEqual(
                    len(segment),
                    parameter.max_length,
                    f"Segment {i} exceeds max length"
                )
                self.assertGreaterEqual(
                    len(segment),
                    parameter.min_length,
                    f"Segment {i} is shorter than min length"
                )

            # 12. 验证 metadata
            self.assertIn("similarity_threshold", result.metadata)
            self.assertEqual(result.metadata["total_segments"], 3)

        except Exception as e:
            print("\nDetailed error information:")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            print("\nFull traceback:")
            import traceback
            print(traceback.format_exc())
            
            # 打印额外的调试信息
            if 'format_result' in locals():
                print("\nFormat split results:")
                for i, seg in enumerate(format_result.segments, 1):
                    print(f"Format segment {i}: {seg[:100]}...")
            
            if 'result' in locals():
                print("\nSemantic split results:")
                for i, seg in enumerate(result.segments, 1):
                    print(f"Semantic segment {i}: {seg[:100]}...")
            
            raise
        
if __name__ == '__main__':
    unittest.main(verbosity=2)