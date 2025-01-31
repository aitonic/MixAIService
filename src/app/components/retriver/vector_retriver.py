from ..store.dto import VectorBacthQueryParameter
from ..store.vector_base import AbsVectorStore
from .base import AbsRetriver
from .dto import MatchInfo, RetriverQuery, RetriverResult


class VectorRetriver(AbsRetriver):

    def __init__(self, vector_store: AbsVectorStore) -> None:
        self.vector_store = vector_store

    async def retrieve(self, query: RetriverQuery) -> RetriverResult:

        vector_results = self.vector_store.batch_query(VectorBacthQueryParameter(
            query_text=query.query,
            top_k=query.top_k,
            filter=query.filter,
            include_metadata=query.include_metadata
        ))
        
        if not vector_results:
            return RetriverResult(results=[])
        
        # Get indices of distances that meet the criteria
        
        results = []
        for result in vector_results:
            indices = {}
            for i, distance in enumerate(result.distances):
                if (1-distance) >= query.score:
                    indices[i] = 1-distance
            metadatas = [MatchInfo(score=indices[i], content=result.metadatas[i]["content"]) for i in indices.keys()]
            results.extend(metadatas)
        return RetriverResult(results=results)
