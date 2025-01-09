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


class EmbeddingFunc(BaseModel):
    embedding_func:object


class VectorRetriverResult(BaseModel):
    ids:list[list[str]] = Field(description="查询结果的id列表")
    # embeddings = Field(default=None)
    metadatas:list[list[dict]] = Field(description="元素据，根据id排序")
    distances:list[list[float]] = Field(description="分数，根据id排序")
