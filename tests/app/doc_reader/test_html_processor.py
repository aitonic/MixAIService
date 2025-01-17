import unittest
from pathlib import Path
import os
import asyncio

# from src.app.model_components.model.dto import ModelResponse
# from src.app.model_components.model.dto import BaseCompletionParameter, BaseMessage

from src.app.model_components.doc_reader.html_reader import HTMLDocReader
from src.app.model_components.model.openai_style import (
    OpenAiStyleLLMParameter,
    OpenAiStyleModel,
)

    
class TestHTMLDocReader(unittest.TestCase):
    """Test cases for HTMLDocReader class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            "model": "readerlm",
            "api_key": "123",
            "base_url": "http://192.168.11.11:8070"
        }
        
        # 创建 OpenAiStyleModel 实例
        llm_model = OpenAiStyleModel(
            OpenAiStyleLLMParameter(**self.config)
        )
        
        # 使用 LLM 模型实例创建 HTMLDocReader
        self.reader = HTMLDocReader(
            llm_model=llm_model,
            max_tokens=8192,
            temperature=0
        )
        # 设置测试文件路径
        self.test_file_path = "/Users/Documents/Google.html"
        
        self.invalid_file_path = "/Users/Documents/test.txt"
        self.nonexistent_file_path = "/Users/Documents/nonexistent.html"


    def test_read_html_content_success(self):
        """测试成功读取HTML文件内容."""
        try:
            content = self.reader.read_data(self.test_file_path)
            self.assertIsInstance(content, str)
            self.assertGreater(len(content), 0)
            print(f"Successfully read HTML content, length: {len(content)}")
        except Exception as e:
            self.fail(f"读取HTML文件失败: {str(e)}")

    # def test_read_html_content_file_not_found(self):
    #     """测试文件不存在的情况."""
    #     with self.assertRaises(FileNotFoundError):
    #         self.reader.read_data(self.nonexistent_file_path)

    # def test_read_html_content_invalid_extension(self):
    #     """测试无效文件扩展名的情况."""
    #     with self.assertRaises(ValueError):
    #         self.reader.read_data(self.invalid_file_path)

    def test_process_content(self):
        """测试实际的内容处理."""
        try:
            # 首先读取HTML内容
            print(f"文件路径:{self.test_file_path}")
            
            result = self.reader.process_content(self.test_file_path)
            
            # 测试实际的处理
            # prompt = "总结下面的内容要点："
            # result = self.reader.process_content(content, prompt)
            
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            print(f"Processing result: {result[:200]}...")  # 打印前200个字符
            
        except Exception as e:
            self.fail(f"处理内容失败: {str(e)}")

    # def test_process_content_with_empty_content(self):
    #     """测试空内容的处理."""
    #     # prompt = "分析下面的内容："
    #     result = self.reader.process_content("")
    #     self.assertIsInstance(result, str)



def main():
    # 设置更详细的测试输出
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main()