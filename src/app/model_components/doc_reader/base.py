from abc import ABC, abstractmethod
from typing import Any

from ..base_component import BaseComponent


class BaseDocReader(BaseComponent, ABC):
    """DocReader 组件的抽象基类，继承自 BaseComponent。
    
    可读取各种输入文件/数据内容，并最终将其转换为 Markdown 格式。
    """

    def __init__(self, name: str = "BaseDocReader") -> None:
        super().__init__(name=name)

    @abstractmethod
    def read_data(self, source: str | bytes) -> str | bytes:
        """读取并返回原始内容，可以是文本、字节流等。

        Args:
            source (Union[str, bytes]): 数据源，可以是文件路径、URL、字节流等。

        Returns:
            Union[str, bytes]: 读取的原始内容。

        """
        pass

    @abstractmethod
    def parse_content(self, raw_content: str | bytes) -> dict[str, Any]:
        """对原始内容进行解析，可根据具体文档类型做结构化处理。

        Args:
            raw_content (Union[str, bytes]): 原始内容，可以是文本或字节流。

        Returns:
            dict[str, Any]: 返回的中间数据结构。

        """
        pass

    @abstractmethod
    def to_markdown(self, parsed_data: dict[str, Any]) -> str:
        """将解析后的数据转为 Markdown 格式并返回。

        Args:
            parsed_data (dict[str, Any]): 解析后的中间数据结构。

        Returns:
            str: 转换后的 Markdown 文本。

        """
        pass

    def process(self, source: str | bytes) -> str:
        """主流程：从读取到转换。对外只需调用此方法即可获取最终 Markdown。

        Args:
            source (Union[str, bytes]): 数据源，可以是文件路径、URL、字节流等。

        Returns:
            str: 转换后的 Markdown 文本。

        """
        raw_content = self.read_data(source)
        parsed_data = self.parse_content(raw_content)
        markdown_result = self.to_markdown(parsed_data)
        return markdown_result
