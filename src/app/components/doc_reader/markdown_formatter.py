# markdown_formatter.py
from typing import Any

from src.utils.logger import logger
from src.app.components.model.dto import BaseCompletionParameter, BaseMessage
from src.app.components.model.openai_style import OpenAiStyleModel


class MarkdownFormatter:
    """Convert data to Markdown format using LLM."""
    
    def __init__(
        self,
        llm_model: OpenAiStyleModel,
        parameter: BaseCompletionParameter
    ) -> None:
        """Initialize MarkdownFormatter with an LLM model and parameters.

        Args:
            llm_model (OpenAiStyleModel): Instance of the language model to be used for formatting.
            parameter (BaseCompletionParameter): Parameters for completion, including model name,
                maximum tokens, and temperature.

        """
        self.llm_model = llm_model
        self.model = parameter.model
        self.max_tokens = parameter.max_new_tokens
        self.temperature = parameter.temperature

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
            model=self.model,
            messages=messages,
            max_new_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=False  # 确保不使用流式返回
        )
        
        try:
            # Process generator responses
            for response in self.llm_model.generate(parameter):
                # Type and attribute checking
                if not hasattr(response, 'choices'):
                    continue
                    
                if not response.choices:
                    continue
                    
                choice = response.choices[0]
                if not hasattr(choice, 'message') or not hasattr(choice.message, 'content'):
                    continue
                    
                return choice.message.content
                
            return ""  # Return empty string if no valid response
            
        except Exception as e:
            logger.error(f"Error processing LLM response: {str(e)}")
            return ""  # Return empty string on error
    

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

