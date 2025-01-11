from collections.abc import Callable

from pydantic import BaseModel, Field

# from typing import Optional

DEFAULT_COLECCTION = "default_collection"

class VectorAddParameter(BaseModel):
    text: str = Field(description="做embedding的文本")
    collection_name: str = Field(default=DEFAULT_COLECCTION)
    embed_function:object = None


class VectorQueryParameter(BaseModel):
    query_text: str 
    collection_name: str = Field(default=DEFAULT_COLECCTION)
    embed_function:object = None

class VectorBacthQueryParameter(BaseModel):
    query_text: str 
    search_collections: list[str] = Field(default=[DEFAULT_COLECCTION])
    embed_function:object = None


class VectorRetriverResult(BaseModel):
    collection_name:str = Field(description="查询的库名")
    ids:list[list[str]] = Field(description="查询结果的id列表")
    # embeddings = Field(default=None)
    metadatas:list[list[dict]] = Field(description="元素据，根据id排序")
    distances:list[list[float]] = Field(description="分数，根据id排序")


class VectorParameter(BaseModel):
    embedding_func:Callable | None = Field(default=None, description="embedding的实例")
    collection_name:str = Field(default=DEFAULT_COLECCTION, description="添加数据时候使用的集合名")
    search_collections:list[str] = Field(default=[DEFAULT_COLECCTION], description="检索时，使用的集合")
