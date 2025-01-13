import traceback
from abc import ABC, abstractmethod

from src.utils import identifier_util
from src.utils.logger import logger

from ..base_component import BaseComponent
from .dto import (
    # DEFAULT_COLECCTION, 
    VectorAddParameter,
    VectorBacthQueryParameter,
    VectorParameter,
    VectorQueryParameter,
    VectorRetriverResult,
)


class AbsVectorStore(ABC, BaseComponent):

    @abstractmethod
    def create_client(self, parameter: VectorParameter) -> bool:
        """创建 ChromaVectorStore 实例并返回客户端。

        Args:
            parameter (VectorParameter): 含有创建客户端所需信息的参数对象。

        Returns:
            bool: 表示客户端创建是否成功。

        Raises:
            ValueError: 如果参数无效或客户端创建失败，将抛出异常。

        """
        pass
    
    @abstractmethod
    def create_collection(self, collection_name:str) -> bool:
        """创建集合的方法，返回布尔值表示是否成功。

        Args:
            collection_name (str): 要创建的集合名称。

        Returns:
            bool: 如果集合创建成功返回 True，否则返回 False。

        """
        pass

    @abstractmethod
    def add_text(self, parameter:VectorAddParameter) -> str:
        """添加文本到指定集合的方法，返回布尔值表示是否成功。

        Args:
            parameter (VectorAddParameter): 包含要添加的文本、集合名称和嵌入函数的参数。

        Returns:
            str: 如果成功，返回添加文本的 ID；否则返回 None。

        Raises:
            如果集合不存在，将抛出异常。

        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name:str) -> bool:
        pass

    @abstractmethod
    def query(self, parameter: VectorQueryParameter) -> VectorRetriverResult:
        """查询指定集合的方法，返回查询结果。

        Args:
            parameter (VectorQueryParameter): 包含查询参数的信息，包括查询文本、集合名称，以及嵌入函数。

        Returns:
            VectorRetriverResult: 查询结果，包含与查询文本相关的前5个结果。

        Raises:
            Exception: 如果指定的集合不存在，将抛出异常。

        """
        pass

    # 生成唯一ID的方法，支持可选前缀
    def get_id(self, prefix: str = None) -> str:
        # 使用前缀生成UUID
        uuid = identifier_util.generate_by_uuid()
        # 如果提供了前缀，则返回前缀和UUID的组合
        if prefix:
            return f"{prefix}-{uuid}"
        
        return uuid  # 返回生成的UUID
    
    def batch_query(self, parameter: VectorBacthQueryParameter) -> list[VectorRetriverResult]:
        
        result = []
        for col in parameter.search_collections:
            try:
                result.append(self.query(VectorQueryParameter(query_text=parameter.query_text, 
                                                          collection_name=col, 
                                                          embed_function=parameter.embed_function,
                                                          result_count=parameter.result_count)))
            except Exception as e:
                logger.error(f"从collection:{col}  中检索数据出错：{traceback.format_exc()}")
        
        return result
            
