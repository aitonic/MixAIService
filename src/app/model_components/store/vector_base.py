from abc import ABC, abstractmethod

from ..base_component import BaseComponent
from .dto import (
    # DEFAULT_COLECCTION, 
    VectorAddParameter,
    VectorQueryParameter,
    VectorRetriverResult,
)
from src.utils import identifier_util

class AbsVectorStore(ABC, BaseComponent):

    @abstractmethod
    def create_client(self, embedding_func:object = None) -> bool:
        """创建 ChromaVectorStore 实例并返回客户端。
    
        Args:
            embedding_func (Callable, optional): 可选的嵌入函数。如果提供，将用于生成嵌入。
    
        Returns:
            bool: 如果创建成功返回 True，否则返回 False。

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