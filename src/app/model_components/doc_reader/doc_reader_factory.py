import os

from .structured_reader import StructuredDocReader
from .unstructured_reader import UnstructuredDocReader


class DocReaderFactory:
    """工厂类，用于根据文件类型或其他逻辑自动选择合适的 Reader。
    """

    @staticmethod
    def get_reader(source: str | dict | list) -> StructuredDocReader | UnstructuredDocReader:
        """根据输入数据类型获取适当的文档读取器。

        Args:
            source (Union[str, dict, list]): 数据源，可能是文件路径字符串、字典或列表。

        Returns:
            Union[StructuredDocReader, UnstructuredDocReader]: 返回适当的文档读取器实例。

        Raises:
            ValueError: 如果输入的 `source` 类型不受支持，将抛出异常。

        """
        if isinstance(source, str) and os.path.isfile(source):
            # 根据文件后缀做简单判定
            if source.endswith(".csv") or source.endswith(".json"):
                return StructuredDocReader()
            else:
                # 假设其他都当做非结构化
                return UnstructuredDocReader()
        else:
            # 可能是纯文本、网络链接、或者字典/列表数据
            # 做更精细的判定
            if isinstance(source, dict | list):   # 合并 isinstance 调用
                return StructuredDocReader()
            elif isinstance(source, str):
                return UnstructuredDocReader()
            else:
                raise ValueError("Unsupported data source type.")
