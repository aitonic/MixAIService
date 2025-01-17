from ..base_component import BaseComponent, BaseFactory
from .chroma_vector_store import ChromaRetriverStore, ChromaUpsertStore


class VectorFactory(BaseFactory):

    def get_bean(self, param: dict) -> BaseComponent:
        component_type = param["component_type"]
        if component_type == "add":
            return ChromaUpsertStore(embedding_func = param["embedding_func"])
        elif component_type == "retriver":
            return ChromaRetriverStore(embedding_func = param["embedding_func"])
        else:
            raise Exception(f"Unimplemented vector store component_type :{component_type}")
