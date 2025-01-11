import csv
import json
import os
from typing import Any

from .base_reader import BaseDocReader
from .markdown_formatter import MarkdownFormatter


class StructuredDocReader(BaseDocReader):
    """用于读取结构化文件的示例 Reader，如 CSV、JSON 等。
    """

    def __init__(self, name: str = "StructuredDocReader") -> None:
        super().__init__(name=name)

    def read_data(self, source: str | list | dict) -> list | dict:
        """根据文件后缀或外部标志，自动识别读取 CSV、JSON 等格式的数据。

        Args:
            source (Union[str, list, dict]): 数据源，可以是文件路径字符串、Python 列表或字典。

        Returns:
            Union[list, dict]: 解析后的数据，可能是列表或字典。

        Raises:
            ValueError: 如果文件格式不支持或 `source` 格式无法识别，将抛出异常。

        """
        if isinstance(source, str) and os.path.isfile(source):
            if source.endswith(".csv"):
                return self._read_csv_file(source)
            elif source.endswith(".json"):
                return self._read_json_file(source)
            else:
                raise ValueError("Unsupported structured file format.")
        elif isinstance(source, list):
            # 假设直接传入 Python 列表等
            return source
        elif isinstance(source, dict):
            # 假设直接传入 Python 字典
            return source
        else:
            raise ValueError("Unrecognized source format for structured data.")

    def parse_content(self, raw_content: dict | list) -> dict[str, Any]:
        """对原始内容进行解析，封装为中间数据结构。

        Args:
            raw_content (dict | list): 原始内容，可能是字典或列表（如 CSV 或 JSON 数据）。

        Returns:
            dict[str, Any]: 包含内容类型和数据的封装字典。

        Raises:
            ValueError: 如果 `raw_content` 格式不受支持，将抛出异常。

        """
        if isinstance(raw_content, dict):
            # 例如 JSON 对象
            return {"type": "dict", "data": raw_content}
        elif isinstance(raw_content, list):
            # 可能是 CSV 或 JSON array
            if all(isinstance(x, dict) for x in raw_content):
                return {"type": "list_of_dict", "data": raw_content}
            else:
                return {"type": "list", "data": raw_content}
        else:
            raise ValueError("Unsupported raw_content format.")


    
    def to_markdown(self, parsed_data: dict[str, Any]) -> str:
        """根据解析结果的 type 使用不同的 MarkdownFormatter 转换逻辑。
        """
        data_type = parsed_data.get("type")
        data = parsed_data.get("data")

        if data_type == "dict":
            # 转成 Markdown 的 key-value 列表
            return MarkdownFormatter.convert_key_values(data)
        elif data_type == "list_of_dict":
            # 转成 Markdown 表格
            return MarkdownFormatter.convert_table(data)
        elif data_type == "list":
            # 简单地把每个元素都当做段落
            return MarkdownFormatter.convert_paragraphs([str(x) for x in data])
        else:
            raise ValueError("Unsupported data type for markdown conversion.")

    def _read_csv_file(self, filepath: str) -> list[dict[str, Any]]:
        """CSV 文件解析
        """
        rows = []
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
        return rows

    def _read_json_file(self, filepath: str) -> dict | list:
        """解析 JSON 文件。

        Args:
            filepath (str): JSON 文件的路径。

        Returns:
            Union[dict, list]: 解析后的 JSON 数据，可以是字典或列表。

        """
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
