import csv
import json
import os
from typing import Any

from .base import BaseDocReader
from .markdown_formatter import MarkdownFormatter


class StructuredDocReader(BaseDocReader):
    """Example Reader for structured files such as CSV, JSON, etc.
    """

    def __init__(self, name: str = "StructuredDocReader") -> None:
        super().__init__(name=name)

    def read_data(self, source: str | list | dict) -> list | dict:
        """Automatically identify and read data in formats like CSV, JSON based on file extension or external flags.

        Args:
            source (str | list | dict): Data source, can be a file path string, Python list or dictionary.

        Returns:
            list | dict: Parsed data, could be a list or dictionary.

        Raises:
            ValueError: Will raise an exception if the file format is not supported or the `source` format is unrecognized.

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
        """Parse raw content and encapsulate it into an intermediate data structure.

        Args:
            raw_content (dict | list): Raw content, which could be a dictionary or list (e.g., CSV or JSON data).

        Returns:
            dict[str, Any]: Encapsulated dictionary containing content type and data.

        Raises:
            ValueError: If the format of `raw_content` is not supported, an exception will be raised.
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
        """Convert parsed data to markdown format using different MarkdownFormatter logic based on the type.

        Args:
            parsed_data (dict[str, Any]): Parsed data containing type and data fields.

        Returns:
            str: Markdown formatted string based on the data type.
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
        """CSV resolve
        """
        rows = []
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
        return rows

    def _read_json_file(self, filepath: str) -> dict | list:
        """Parse JSON file.

        Args:
            filepath (str): Path to the JSON file.

        Returns:
            Union[dict, list]: Parsed JSON data, which can be either a dictionary or a list.

        """
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
