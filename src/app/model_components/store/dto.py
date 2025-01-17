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
    result_count:int = 5

class VectorBacthQueryParameter(BaseModel):
    query_text: str 
    search_collections: list[str] = Field(default=[DEFAULT_COLECCTION])
    embed_function:object = None
    result_count:int = 5


class VectorRetriverResult(BaseModel):
    collection_name: str = Field(description="Name of the queried collection")
    ids: list[list[str]] = Field(description="List of IDs for query results")
    # embeddings = Field(default=None)
    metadatas: list[list[dict]] = Field(description="Metadata sorted by ID")
    distances: list[list[float]] = Field(description="Scores sorted by ID")

    @classmethod
    def empty(cls, collection_name:str = DEFAULT_COLECCTION) -> "VectorRetriverResult":
        return VectorRetriverResult(collection_name=collection_name, ids=[], metadatas=[], distances=[])


class VectorParameter(BaseModel):
    embedding_func:Callable | None = Field(default=None, description="Instance of embedding function")
    collection_name:str = Field(default=DEFAULT_COLECCTION, description="Collection name used when adding data")
    search_collections:list[str] = Field(default=[DEFAULT_COLECCTION], description="Collections used during retrieval")
