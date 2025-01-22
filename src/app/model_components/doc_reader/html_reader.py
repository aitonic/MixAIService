# html_reader.py
from pathlib import Path
from typing import Any

from src.app.model_components.model.dto import BaseCompletionParameter
from src.app.model_components.model.openai_style import OpenAiStyleModel
from src.app.model_components.web_scraper.dto import ScraperResult
from src.utils.exceptions import DocumentNotFoundError
from src.utils.html_converter import HTMLConverter

from .base import BaseDocReader
from .markdown_formatter import MarkdownFormatter


class HTMLDocReader(BaseDocReader):
    """HTML document processor that integrates with OpenAI API."""
    
    def __init__(
        self,
        llm_model: OpenAiStyleModel,  
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
        
        # Create an instance of BaseCompletionParameter with default values.
        parameter = BaseCompletionParameter(
            model="readerlm",  # The model name, or retrieve it from configuration.
            messages=[],  # Initialize with an empty list, to be populated during use.
            max_new_tokens=max_tokens,  # The maximum number of tokens to generate.
            temperature=temperature,  # The temperature parameter for generation.
            stream=False  # Whether to enable streaming mode.
        )

        # Initialize the MarkdownFormatter using the updated approach.
        self.markdown_formatter = MarkdownFormatter(
            llm_model=llm_model,  # The language model instance.
            parameter=parameter  # The configuration parameters for the formatter.
        )

    def read_data(self, source: str | ScraperResult) -> str:
            """Read HTML content from the specified file path or ScraperResult.

            Args:
                source (str | ScraperResult): Path to the HTML file or ScraperResult object

            Returns:
                str: Raw HTML content

            Raises:
                FileNotFoundError: If the HTML file does not exist
                ValueError: If the file is not an HTML file
                ValueError: If the ScraperResult indicates a failure

            """
            if isinstance(source, ScraperResult):
                if not source.success:
                    raise ValueError(f"Scraping failed: {source.error_message}")
                if source.content is None:
                    raise ValueError("ScraperResult content is None")
                return source.content

            path = Path(source)
            
            if not path.exists():
                raise DocumentNotFoundError(f"File not found: {source}")
                
            if path.suffix.lower() not in ['.html', '.htm']:
                raise ValueError(f"File must be HTML format: {source}")
                
            with open(source, encoding='utf-8') as file:
                return file.read()
                
    def parse_content(self, raw_content: str) -> dict[str, Any]:
        """Parse HTML content into structured format.
        
        Args:
            raw_content (str): Raw HTML content

        Returns:
            dict[str, Any]: Parsed content with 'content' key

        """
        cleaned_content = HTMLConverter.clean_html(raw_content)
        # return {"content": cleaned_content}
        return cleaned_content

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
        return self.to_markdown(parsed_content, prompt)


