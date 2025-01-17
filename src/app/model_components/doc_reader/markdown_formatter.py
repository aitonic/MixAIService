# markdown_formatter.py

from src.app.model_components.model.dto import BaseCompletionParameter, BaseMessage
from src.app.model_components.model.openai_style import OpenAiStyleModel


class MarkdownFormatter:
    """Helper class for converting data to Markdown format using LLM."""
    
    def __init__(
        self,
        llm_model : OpenAiStyleModel,
        parameter : BaseCompletionParameter
    ) -> None:
        """Initialize MarkdownFormatter with LLM model.

        Args:
            llm_model (OpenAiStyleModel): LLM model instance
            max_tokens (int, optional): Maximum tokens for completion. Defaults to 8192.
            temperature (float, optional): Temperature for generation. Defaults to 0.

        """
        self.llm_model = llm_model
        self.model = parameter.model
        self.max_tokens = parameter.max_new_tokens
        self.temperature = parameter. temperature

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
        
        # 处理生成器返回值
        for response in self.llm_model.generate(parameter):
            if not response.choices or len(response.choices) == 0:
                continue
            return response.choices[0].message.content
            
        return ""  # 如果没有有效响应，返回空字符串

