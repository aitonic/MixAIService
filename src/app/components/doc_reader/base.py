from abc import ABC, abstractmethod

from src.app.components.web_scraper.dto import ScraperResult

from ..base_component import BaseComponent


class BaseDocReader(BaseComponent, ABC):
    """Abstract base class for DocReader components, inheriting from BaseComponent.
    
    This class can read various input files/data content and convert them to Markdown format.
    """

    source: str | bytes | ScraperResult

    def __init__(self, name: str = "BaseDocReader") -> None:
        super().__init__(name=name)

    @abstractmethod
    def read_data(self, source: str | bytes | ScraperResult) -> str | bytes:
        """Read and return the raw content, which can be text, byte streams, etc.

        Args:
            source (Union[str, list, dict]): Data source, such as file path, URL, or structured data.

        Returns:
            Union[str, bytes]: The raw content read from the source.

        """
        pass

    @abstractmethod
    def parse_content(self, raw_content: str | bytes) -> dict[str, str | list | dict]:
        """Parse the raw content into a structured format based on the document type.

        Args:
            raw_content (Union[str, bytes]): Raw content, which can be text or byte streams.

        Returns:
            dict[str, Union[str, list, dict]]: Intermediate data structure for further processing.

        """
        pass

    @abstractmethod
    def to_markdown(self, parsed_data: dict[str, str | list | dict]) -> str:
        """Convert the parsed data to Markdown format and return the result.

        Args:
            parsed_data (dict[str, Union[str, list, dict]]): Parsed data structure.

        Returns:
            str: Converted Markdown text.

        """
        pass

    def process(self, source: str | bytes | ScraperResult) -> str:
        """Process the source by reading and converting it to Markdown.

        This method handles the entire workflow, from reading the input 
        to converting it into Markdown format. Users only need to call 
        this method to get the final output.

        Args:
            source (str | bytes | ScraperResult): The data source, such as a file path, URL, byte stream, or ScraperResult object.

        Returns:
            str: The converted Markdown text.

        """
        raw_content = self.read_data(source)
        parsed_data = self.parse_content(raw_content)
        markdown_result = self.to_markdown(parsed_data)
        return markdown_result

    def __call__(self, *args: tuple[dict[str, str | list | dict], ...], **kwds: dict) -> str:
        """Callable method to process the input data and return Markdown output.

        Args:
            *args (tuple[dict[str, Union[str, list, dict]], ...]): Arguments containing input data.
            **kwds (dict): Additional keyword arguments.

        Returns:
            str: The processed Markdown output.

        """
        arg = args[0]
        if "source" in arg:
            return self.process(arg["source"])
        else:
            return self.process(arg["query"])
