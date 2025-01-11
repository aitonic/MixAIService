# from pydantic import BaseModel, Field

import os
from collections.abc import Callable
from typing import Any

import chromadb
from chromadb import Settings
from chromadb.api import ClientAPI

from .dto import (
    # DEFAULT_COLECCTION, 
    VectorAddParameter,
    VectorBacthQueryParameter,
    VectorQueryParameter,
    VectorRetriverResult,
)
from .vector_base import AbsVectorStore


class ChromaVectorStore(AbsVectorStore):

    __client:ClientAPI

    def __init__(self, embedding_func:object = None) -> None:
        super().__init__()
        chromadb_client = chromadb.Client(
            Settings(
                # chroma_db_impl='duckdb+parquet',
                chroma_server_host=os.getenv("CHROMA_HOST", "localhost").strip(),
                chroma_server_http_port=int(os.getenv("CHROMA_PORT", "8000").strip()),
                persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "/chromadb/persist/").strip(),
                is_persistent = True,
                allow_reset  =True
            )
        )

        self.__client = chromadb_client  # 设置实例的 __client 属性
        if embedding_func:
            self.embedding_func = embedding_func
    
    @classmethod
    def create_client(cls, embedding_func: Callable | None = None) -> "ChromaVectorStore":
        """创建 ChromaVectorStore 实例并返回客户端。

        Args:
            embedding_func (Callable, optional): 可选的嵌入函数。如果提供，将用于生成嵌入。

        Returns:
            ChromaVectorStore: 返回创建的 ChromaVectorStore 实例。

        """
        return ChromaVectorStore(embedding_func=embedding_func)
    
    def __embedding(self, text: str, embed_function: Callable[[str], list[float]] | None = None) -> list[float]:
        """生成文本的嵌入向量。

        Args:
            text (str): 输入文本。
            embed_function (Callable[[str], list[float]], optional): 可选的嵌入函数，用于生成嵌入向量。如果未提供，将使用默认逻辑。

        Returns:
            list[float]: 生成的嵌入向量。

        """
        # 使用提供的嵌入函数生成嵌入向量
        if embed_function:
            embeddings = embed_function({"query": text})
        # 使用类的嵌入函数生成嵌入向量
        elif self.embedding_func:
            embeddings = self.embedding_func({"query": text})
        else:
            return []  # 如果没有提供嵌入函数，返回空列表

        return embeddings[0]["embedding"] if embeddings else []  # 返回生成的嵌入向量

    # 创建集合的方法，返回布尔值表示是否成功
    def create_collection(self, collection_name:str) -> bool:
        """创建集合的方法，返回布尔值表示是否成功。

        Args:
            collection_name (str): 要创建的集合名称。

        Returns:
            bool: 如果集合创建成功返回 True，否则返回 False。

        """
        try:
            self.__client.get_or_create_collection(name=collection_name)
        except Exception:
            return False
        return True

    # 添加文本到指定集合的方法，返回布尔值表示是否成功
    def add_text(self, parameter:VectorAddParameter) -> str:
        """添加文本到指定集合的方法，返回布尔值表示是否成功。

        Args:
            parameter (VectorAddParameter): 包含要添加的文本、集合名称和嵌入函数的参数。

        Returns:
            str: 如果成功，返回添加文本的 ID；否则返回 None。

        Raises:
            如果集合不存在，将抛出异常。

        """
        collection = self.__client.get_or_create_collection(name=parameter.collection_name)

        if not collection:
            return None
        
        embed_result = self.__embedding(parameter.text, parameter.embed_function)
        
        id = self.get_id(prefix=parameter.collection_name)
        # 添加文本到集合
        collection.add(
            ids=id,
            embeddings=embed_result,
            metadatas=[{"source": parameter.text}]
        )
        return id  # 返回成功

    # 删除指定集合的方法，返回布尔值表示是否成功
    def delete_collection(self, collection_name: str) -> bool:
        """删除指定集合的方法，返回布尔值表示是否成功。

        Args:
            collection_name (str): 要删除的集合名称。

        Returns:
            bool: 如果集合删除成功返回 True，否则返回 False。

        """
        try:
            self.__client.delete_collection(name=collection_name)
        except Exception:
            return False
        return True  # 返回成功

    # 查询指定集合的方法，返回查询结果
    def query(self, parameter:VectorQueryParameter) -> VectorRetriverResult:
        """查询指定集合的方法，返回查询结果。

        Args:
            parameter (VectorQueryParameter): 包含查询文本、集合名称和嵌入函数的参数对象。

        Returns:
            VectorRetriverResult: 查询结果，包含与查询文本相关的前5个结果。

        Raises:
            Exception: 如果指定的集合不存在，将抛出异常。

        """
        collection = self.__client.get_collection(name=parameter.collection_name)

        if not collection:
            raise Exception(f"collection is not exsit : {parameter.collection_name}")
        
        embed_result = self.__embedding(parameter.query_text, parameter.embed_function)

        # 执行查询
        results = collection.query(
            query_embeddings=embed_result,
            n_results=5  # 返回前5个结果
        )
        results["collection_name"] = parameter.collection_name
        
        return VectorRetriverResult(**results)  # 返回查询结果
    
class ChromaUpsertStore(ChromaVectorStore):
    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> str:
        """添加文本向量的调用方法。

        Args:
            *args (tuple[dict[str, Any], ...]): 包含向量添加参数的字典元组。
            **kwds (dict[str, Any]): 其他可选关键字参数（当前未使用）。

        Returns:
            str: 添加文本后的结果。

        """
        params = args[0]  # 获取第一个参数字典
        return self.add_text(VectorAddParameter(**params))
    

class ChromaRetriverStore(ChromaVectorStore):

    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> list[VectorRetriverResult]:
        """添加文本向量的调用方法。

        Args:
            *args (tuple[dict[str, Any], ...]): 包含向量添加参数的字典元组。
            **kwds (dict[str, Any]): 其他可选关键字参数（当前未使用）。

        Returns:
            str: 添加文本后的结果。

        """
        params = args[0]  # 获取第一个参数字典
        parameter = VectorBacthQueryParameter(**params)
        return self.batch_query(parameter)
