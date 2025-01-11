from typing import Any


class MarkdownFormatter:
    """辅助类：将结构化或非结构化的数据转换为 Markdown 字符串。
    """

    @staticmethod
    def convert_paragraphs(paragraphs: list[str]) -> str:
        """将一系列段落转换为 Markdown 格式（简单示例）。
        """
        return "\n\n".join(paragraphs)

    @staticmethod
    def convert_table(table_data: list[dict[str, Any]]) -> str:
        """将结构化数据(例如 CSV 解析后的列表) 转换为 Markdown 表格。
        
        table_data: List[Dict[str, Any]]，如:
            [{"name": "Alice", "age": 18}, {"name": "Bob", "age": 20}]
        """
        if not table_data:
            return ""

        headers = list(table_data[0].keys())
        header_row = "| " + " | ".join(headers) + " |"
        split_row = "| " + " | ".join(["---"] * len(headers)) + " |"

        body_rows = []
        for row in table_data:
            row_cells = [str(row[h]) for h in headers]
            body_rows.append("| " + " | ".join(row_cells) + " |")

        return "\n".join([header_row, split_row] + body_rows)

    @staticmethod
    def convert_key_values(data: dict[str, Any]) -> str:
        """将键值对转为 Markdown 列表或其他合适格式。只作演示示例。
        """
        lines = []
        for key, value in data.items():
            lines.append(f"- **{key}**: {value}")
        return "\n".join(lines)
