from abc import ABC, abstractmethod

from ..base_component import BaseComponent
from .dto import (
    RetriverQuery,
    RetriverResult,
)


class AbsRetriver(ABC, BaseComponent):
    """Retrieve information.
    Search for matching content lists from specified sources based on input information
    and other specified parameters (to be handled by respective implementations).
    """

    @abstractmethod
    async def retrieve(self, query: RetriverQuery) -> RetriverResult:
        """根据查询内容检索相关信息
        
        Args:
            query: 查询字符串
            top_k: 返回结果的最大数量
            
        Returns:
            返回与查询最相关的top_k个结果，每个结果为字符串格式

        """
        pass


    async def __call__(self, param:dict) -> RetriverResult:
        """Call method for retrieving information.
        
        Args:
            query: 查询字符串
            top_k: 返回结果的最大数量
            
        Returns:
            返回与查询最相关的top_k个结果，每个结果为字符串格式

        """
        return await self.retrieve(RetriverQuery(
            query=param.get("query"),
            top_k=param.get("top_k", 5),
            search_keys=param.get("search_keys", []),
            meta_data=param.get("meta_data", {})
        ))
