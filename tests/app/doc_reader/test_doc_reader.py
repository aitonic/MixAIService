import os
import unittest
import tempfile
from src.app.components.doc_reader.unstructured_reader import UnstructuredDocReader
from src.app.components.doc_reader.structured_reader import StructuredDocReader
from src.app.components.doc_reader.doc_reader_factory import DocReaderFactory


class TestDocReader(unittest.TestCase):
    """
    使用 unittest 对 doc_reader 组件进行单元测试。
    包含对 UnstructuredDocReader、StructuredDocReader 以及 DocReaderFactory 的测试。
    """

    def setUp(self):
        """
        在每个 test* 方法执行前都会调用，用于初始化通用资源。
        """
        self.unstructured_reader = UnstructuredDocReader()
        self.structured_reader = StructuredDocReader()

    def test_unstructured_reader_with_plain_text(self):
        """
        测试 UnstructuredDocReader 读取纯文本的能力，并检查转换后的 Markdown。
        """
        plain_text = "Hello World\nThis is a test.\n"
        md_result = self.unstructured_reader.process(plain_text)
        self.assertIn("Hello World", md_result, "Markdown 结果应包含原文本内容。")
        self.assertIn("This is a test.", md_result, "Markdown 结果应包含原文本内容。")

    def test_unstructured_reader_with_file(self):
        """
        测试 UnstructuredDocReader 从文件读取文本的能力。
        """
        sample_text = "Line 1\nLine 2\n"
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as tmp_file:
            tmp_file_name = tmp_file.name
            tmp_file.write(sample_text)

        # 验证能否读取文件并转换
        md_result = self.unstructured_reader.process(tmp_file_name)
        self.assertIn("Line 1", md_result, "Markdown 结果应包含文件中的文本。")
        self.assertIn("Line 2", md_result, "Markdown 结果应包含文件中的文本。")

        # 清理临时文件
        if os.path.exists(tmp_file_name):
            os.remove(tmp_file_name)

    def test_structured_reader_with_csv(self):
        """
        测试 StructuredDocReader 读取 CSV 并转换为 Markdown 表格。
        """
        sample_csv = """name,age
Alice,18
Bob,20
"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tmp_file:
            tmp_file_name = tmp_file.name
            tmp_file.write(sample_csv)

        md_result = self.structured_reader.process(tmp_file_name)
        self.assertIn("| name | age |", md_result, "Markdown 表格应包含表头。")
        self.assertIn("Alice", md_result, "Markdown 表格应包含第一行数据。")
        self.assertIn("Bob", md_result, "Markdown 表格应包含第二行数据。")

        if os.path.exists(tmp_file_name):
            os.remove(tmp_file_name)

    def test_structured_reader_with_json_dict(self):
        """
        测试 StructuredDocReader 读取 JSON dict，并输出 Markdown 的键值列表。
        """
        sample_dict = {"key1": "value1", "key2": 123}
        md_result = self.structured_reader.process(sample_dict)

        self.assertIn("**key1**: value1", md_result, "Markdown 结果应包含 JSON 字段 key1 的信息。")
        self.assertIn("**key2**: 123", md_result, "Markdown 结果应包含 JSON 字段 key2 的信息。")

    def test_structured_reader_with_json_file(self):
        """
        测试 StructuredDocReader 从 JSON 文件中读取数据并转换为 Markdown。
        """
        import json
        sample_json = {"name": "Charlie", "score": 95}
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp_file:
            tmp_file_name = tmp_file.name
            json.dump(sample_json, tmp_file)

        md_result = self.structured_reader.process(tmp_file_name)
        self.assertIn("**name**: Charlie", md_result, "Markdown 中应包含 'name' 字段。")
        self.assertIn("**score**: 95", md_result, "Markdown 中应包含 'score' 字段。")

        if os.path.exists(tmp_file_name):
            os.remove(tmp_file_name)

    def test_doc_reader_factory_with_csv(self):
        """
        测试 DocReaderFactory 自动识别 CSV 文件并使用对应的 StructuredDocReader。
        """
        sample_csv = """colA,colB
valA,valB
"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tmp_file:
            tmp_file_name = tmp_file.name
            tmp_file.write(sample_csv)

        reader = DocReaderFactory.get_reader(tmp_file_name)
        self.assertIsInstance(reader, StructuredDocReader, "CSV 文件应被识别为 StructuredDocReader。")
        md_result = reader.process(tmp_file_name)
        self.assertIn("| colA | colB |", md_result, "Markdown 表格应包含表头。")

        if os.path.exists(tmp_file_name):
            os.remove(tmp_file_name)

    def test_doc_reader_factory_with_plain_text(self):
        """
        测试 DocReaderFactory 自动识别普通文本并使用 UnstructuredDocReader。
        """
        text_input = "Just a plain text"
        reader = DocReaderFactory.get_reader(text_input)
        self.assertIsInstance(reader, UnstructuredDocReader, "纯文本应被识别为 UnstructuredDocReader。")
        md_result = reader.process(text_input)
        self.assertIn("Just a plain text", md_result, "Markdown 结果应包含原文本。")


if __name__ == '__main__':
    unittest.main()