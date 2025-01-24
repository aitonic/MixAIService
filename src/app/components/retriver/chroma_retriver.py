from ..store.dto import VectorBacthQueryParameter
from ..store.vector_base import AbsVectorStore
from .base import AbsRetriver
from .dto import RetriverQuery, RetriverResult


class VectorRetriver(AbsRetriver):

    def __init__(self, vector_store: AbsVectorStore) -> None:
        super().__init__("VectorRetriver")
        self.vector_store = vector_store

    async def retrieve(self, query: RetriverQuery) -> RetriverResult:

        self.vector_store.batch_query(VectorBacthQueryParameter(
# query_text: str 
#     search_collections: list[str] = Field(default=[DEFAULT_COLECCTION])
#     embed_function:object = None
#     result_count:int = 5
#     meta_data:dict | None = {}
            query_text=query.query,
            top_k=query.top_k,
            filter=query.filter,
            include_metadata=query.include_metadata
        ))
