# html_reader.py
from pathlib import Path
from typing import Any

from src.app.model_components.model.openai_style import OpenAiStyleModel
from src.utils.html_converter import HTMLConverter

from .base import BaseDocReader
from .markdown_formatter import MarkdownFormatter


class HTMLDocReader(BaseDocReader):
    """HTML document processor that integrates with OpenAI API."""
    
    def __init__(
        self,
        llm_model: OpenAiStyleModel,  # 改为必需参数
        name: str = "HTMLDocReader",
        max_tokens: int = 8192,
        temperature: float = 0
    ) -> None:
        """Initialize HTMLDocReader with LLM model.

        Args:
            llm_model (OpenAiStyleModel): LLM model instance
            name (str, optional): Reader name. Defaults to "HTMLDocReader".
            max_tokens (int, optional): Maximum tokens for completion. Defaults to 8192.
            temperature (float, optional): Temperature for generation. Defaults to 0.

        """
        super().__init__(name=name)
        self.llm_model = llm_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.markdown_formatter = MarkdownFormatter(
            llm_model=llm_model,
            max_tokens=max_tokens,
            temperature=temperature
        )

    def read_data(self, file_path: str) -> str:
        """Read HTML content from the specified file path.

        Args:
            file_path (str): Path to the HTML file

        Returns:
            str: Raw HTML content

        Raises:
            FileNotFoundError: If the HTML file does not exist
            ValueError: If the file is not an HTML file

        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if path.suffix.lower() not in ['.html', '.htm']:
            raise ValueError(f"File must be HTML format: {file_path}")
            
        with open(file_path, encoding='utf-8') as file:
            return file.read()
            
    def parse_content(self, raw_content: str) -> dict[str, Any]:
        """Parse HTML content into structured format.
        
        Args:
            raw_content (str): Raw HTML content

        Returns:
            dict[str, Any]: Parsed content with 'content' key

        """
        cleaned_content = HTMLConverter.clean_html(raw_content)
        return {"content": cleaned_content}

    def to_markdown(self, parsed_data: str, prompt: str = "") -> str:
        """Convert HTML to Markdown using LLM.

        Args:
            parsed_data (str): HTML content to convert
            prompt (str, optional): Custom prompt for LLM. Defaults to "".

        Returns:
            str: Markdown formatted content

        """
        return self.markdown_formatter.convert_html_by_llm(
            content=parsed_data,
            prompt=prompt or "Convert the following HTML to well-formatted Markdown:"
        )

    def process_content(self, file_path: str, prompt: str = "") -> str:
        """Process HTML file to Markdown.

        Args:
            file_path (str): Path to HTML file
            prompt (str, optional): Custom prompt for LLM. Defaults to "".

        Returns:
            str: Processed Markdown content

        """
        raw_content = self.read_data(file_path)
        parsed_content = self.parse_content(raw_content)
        return self.to_markdown(parsed_content["content"], prompt)


