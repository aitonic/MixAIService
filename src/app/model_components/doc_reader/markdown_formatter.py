# markdown_formatter.py
from typing import Any

from src.app.model_components.model.dto import BaseCompletionParameter, BaseMessage
from src.app.model_components.model.openai_style import OpenAiStyleModel


class MarkdownFormatter:
    """Helper class for converting data to Markdown format using LLM."""
    
    def __init__(
        self,
        llm_model: OpenAiStyleModel,
        max_tokens: int = 8192,
        temperature: float = 0
    ) -> None:
        """Initialize MarkdownFormatter with LLM model.

        Args:
            llm_model (OpenAiStyleModel): LLM model instance
            max_tokens (int, optional): Maximum tokens for completion. Defaults to 8192.
            temperature (float, optional): Temperature for generation. Defaults to 0.

        """
        self.llm_model = llm_model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def convert_html_by_llm(self, content: str, prompt: str) -> str:
        """Convert HTML to Markdown using LLM.

        Args:
            content (str): HTML content to convert
            prompt (str): Prompt for the LLM

        Returns:
            str: Converted Markdown content

        """
        messages = [
            BaseMessage(role="system", content=prompt),
            BaseMessage(role="user", content=content)
        ]
        
        parameter = BaseCompletionParameter(
            model="readerlm",
            messages=messages,
            max_new_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=False  # 确保不使用流式返回
        )
        
        # 处理生成器返回值
        for response in self.llm_model.generate(parameter):
            if not response.choices or len(response.choices) == 0:
                continue
            return response.choices[0].message.content
            
        return ""  # 如果没有有效响应，返回空字符串
    

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

