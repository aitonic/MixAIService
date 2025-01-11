import os
from typing import Any

from .base_reader import BaseDocReader
from .markdown_formatter import MarkdownFormatter


class UnstructuredDocReader(BaseDocReader):
    """用于读取非结构化文件的示例 Reader
    """

    def __init__(self, name: str = "UnstructuredDocReader") -> None:
        super().__init__(name=name)

    def read_data(self, source: str) -> str:
        """简单示例读取文本文件，可扩展为 PDF 解析等。
        
        Args:
            source (str): 数据源，可以是文件路径或纯文本。

        Returns:
            str: 读取的数据内容。

        Raises:
            ValueError: 如果 `source` 的格式无法识别。

        """
        if isinstance(source, str) and os.path.isfile(source):
            with open(source, encoding="utf-8") as f:
                return f.read()
        elif isinstance(source, str):
            # 也可能是直接传入纯文本
            return source
        else:
            raise ValueError("Unrecognized source format for unstructured data.")
    
    def parse_content(self, raw_content: str) -> dict[str, Any]:
        """示例做简单段落切分，也可用自然语言处理做进一步拆分。
        
        返回一个键为 paragraphs 的字典，方便后续 Markdown 转换。
        """
        paragraphs = [p.strip() for p in raw_content.split("\n") if p.strip()]
        return {"paragraphs": paragraphs}

    def to_markdown(self, parsed_data: dict[str, Any]) -> str:
        """利用 MarkdownFormatter 将段落转换为 Markdown。
        """
        paragraphs = parsed_data.get("paragraphs", [])
        return MarkdownFormatter.convert_paragraphs(paragraphs)
