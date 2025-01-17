from abc import ABC, abstractmethod
from typing import Any

from ..base_component import BaseComponent
from .dto import Source


class BaseDocReader(BaseComponent, ABC):
    """Abstract base class for DocReader component, inherits from BaseComponent.
    
    Can read various input files/data content and finally convert them to Markdown format.
    """
    source:str | bytes

    def __init__(self, name: str = "BaseDocReader") -> None:
        super().__init__(name=name)

    @abstractmethod
    def read_data(self, source: str | list | dict) -> str | bytes:
        """Read and return raw content, which can be text, byte stream, etc.

        Args:
            source (Union[str, bytes]): Data source, can be file path, URL, byte stream, etc.

        Returns:
            Union[str, bytes]: The raw content read.

        """
        pass

    @abstractmethod
    def parse_content(self, raw_content: str | bytes) -> dict[str, Any]:
        """Parse raw content and perform structured processing based on specific document types.

        Args:
            raw_content (Union[str, bytes]): Raw content, which can be text or byte stream.

        Returns:
            dict[str, Any]: Intermediate data structure after parsing.

        """
        pass

    @abstractmethod
    def to_markdown(self, parsed_data: dict[str, Any]) -> str:
        """Convert parsed data to Markdown format and return.

        Args:
            parsed_data (dict[str, Any]): Intermediate data structure after parsing.

        Returns:
            str: Converted Markdown text.

        """
        pass

    def process(self, source: str | bytes) -> str:
        """Main process: from reading to conversion. Only need to call this method to get the final Markdown.

        Args:
            source (Union[str, bytes]): Data source, can be file path, URL, byte stream, etc.

        Returns:
            str: Converted Markdown text.

        """
        raw_content = self.read_data(source)
        parsed_data = self.parse_content(raw_content)
        markdown_result = self.to_markdown(parsed_data)
        return markdown_result


    def __call__(self, *args: Any, **kwds: Any) -> Any:
        arg = args[0]
        if "source" in arg:
            return self.process(arg["source"])
        else:
            return self.process(arg["query"])