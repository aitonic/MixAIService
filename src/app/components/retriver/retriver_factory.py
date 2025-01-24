from abc import ABC, abstractmethod

from ..base_component import BaseComponent


class AbsRetriver(ABC, BaseComponent):
    """Retrieve information.
    Search for matching content lists from specified sources based on input information
    and other specified parameters (to be handled by respective implementations).
    """

    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """根据查询内容检索相关信息
        
        Args:
            query: 查询字符串
            top_k: 返回结果的最大数量
            
        Returns:
            返回与查询最相关的top_k个结果，每个结果为字符串格式

        """
        pass

    @abstractmethod
    def get_retriever_type(self) -> str:
        """获取检索器类型
        
        Returns:
            返回检索器类型名称

        """
        pass

    @abstractmethod
    def get_retriever_config(self) -> dict:
        """获取检索器配置信息
        
        Returns:
            返回检索器的配置字典

        """
        pass
