# from pydantic import BaseModel, Field

import os
from collections.abc import Callable
from typing import Any

import chromadb
from chromadb import Settings
from chromadb.api import ClientAPI
from chromadb.errors import InvalidCollectionException

from src.utils.logger import logger

from .dto import (
    # DEFAULT_COLECCTION,
    VectorAddParameter,
    VectorBacthQueryParameter,
    VectorQueryParameter,
    VectorRetriverResult,
)
from .vector_base import AbsVectorStore


class ChromaVectorStore(AbsVectorStore):

    __client: ClientAPI

    def __init__(self, embedding_func: object = None) -> None:
        super().__init__()
        chromadb_client = chromadb.Client(
            Settings(
                chroma_server_host=os.getenv("CHROMA_HOST", "localhost").strip(),
                chroma_server_http_port=int(os.getenv("CHROMA_PORT", "8000").strip()),
                persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY", "/chromadb/persist/").strip(),
                is_persistent=True,
                allow_reset=True
            )
        )

        # Set instance's __client attribute
        self.__client = chromadb_client  
        if embedding_func:
            self.embedding_func = embedding_func
    
    @classmethod
    def create_client(cls, embedding_func: Callable | None = None) -> "ChromaVectorStore":
        """Create ChromaVectorStore instance and return client.

        Args:
            embedding_func (Callable, optional): Optional embedding function. If provided, will be used to generate embeddings.

        Returns:
            ChromaVectorStore: Returns created ChromaVectorStore instance.

        """
        return ChromaVectorStore(embedding_func=embedding_func)
    
    def __embedding(self, text: str, embed_function: Callable[[str], list[float]] | None = None) -> list[float]:
        """Generate embedding vector for text.

        Args:
            text (str): Input text.
            embed_function (Callable[[str], list[float]], optional): Optional embedding function to generate embeddings. If not provided, default logic will be used.

        Returns:
            list[float]: Generated embedding vector.

        """
        # Use provided embedding function to generate embeddings
        if embed_function:
            embeddings = embed_function({"query": text})
        # Use class embedding function to generate embeddings
        elif self.embedding_func:
            embeddings = self.embedding_func({"query": text})
        else:
            return []  # Return empty list if no embedding function provided

        return embeddings[0]["embedding"] if embeddings else []  # Return generated embedding vector

    def create_collection(self, collection_name: str) -> bool:
        """Create collection and return boolean indicating success.

        Args:
            collection_name (str): Name of collection to create.

        Returns:
            bool: Returns True if collection created successfully, False otherwise.

        """
        try:
            self.__client.get_or_create_collection(name=collection_name)
        except Exception:
            return False
        return True

    def add_text(self, parameter: VectorAddParameter) -> str:
        """Add text to specified collection and return boolean indicating success.

        Args:
            parameter (VectorAddParameter): Parameter containing text to add, collection name and embedding function.

        Returns:
            str: Returns added text ID if successful, None otherwise.

        Raises:
            Exception: If collection does not exist.

        """
        collection = self.__client.get_or_create_collection(name=parameter.collection_name)

        if not collection:
            return None
        
        embed_result = self.__embedding(parameter.text, parameter.embed_function)
        
        id = self.get_id(prefix=parameter.collection_name)
        # Add text to collection
        collection.add(
            ids=id,
            embeddings=embed_result,
            metadatas=[{"source": parameter.text}]
        )
        return id  # Return success

    def delete_collection(self, collection_name: str) -> bool:
        """Delete specified collection and return boolean indicating success.

        Args:
            collection_name (str): Name of collection to delete.

        Returns:
            bool: Returns True if collection deleted successfully, False otherwise.

        """
        try:
            self.__client.delete_collection(name=collection_name)
        except Exception:
            return False
        return True  # Return success

    def query(self, parameter: VectorQueryParameter) -> VectorRetriverResult:
        """Query specified collection and return query results.

        Args:
            parameter (VectorQueryParameter): Parameter object containing query text, collection name and embedding function.

        Returns:
            VectorRetriverResult: Query results containing top 5 results related to query text.

        """
        try:
            collection = self.__client.get_collection(name=parameter.collection_name)
            
            embed_result = self.__embedding(parameter.query_text, parameter.embed_function)

            # Execute query
            results = collection.query(
                query_embeddings=embed_result,
                n_results=parameter.result_count  # Return top 5 results
            )
            results["collection_name"] = parameter.collection_name
            
            return VectorRetriverResult(**results)  # Return query results
        except InvalidCollectionException:
            # raise Exception(f"collection is not exsit : {parameter.collection_name}")
            logger.warn(f"collection is not exsit : {parameter.collection_name}")
            return VectorRetriverResult.empty(collection_name=parameter.collection_name)

    
class ChromaUpsertStore(ChromaVectorStore):
    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> str:
        """Call method for adding text vectors.

        Args:
            *args (tuple[dict[str, Any], ...]): Tuple of dictionaries containing vector add parameters.
            **kwds (dict[str, Any]): Other optional keyword arguments (currently unused).

        Returns:
            str: Result after adding text.

        """
        params = args[0]  # Get first parameter dictionary
        return self.add_text(VectorAddParameter(**params))
    

class ChromaRetriverStore(ChromaVectorStore):

    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> list[VectorRetriverResult]:
        """Call method for adding text vectors.

        Args:
            *args (tuple[dict[str, Any], ...]): Tuple of dictionaries containing vector add parameters.
            **kwds (dict[str, Any]): Other optional keyword arguments (currently unused).

        Returns:
            str: Result after adding text.

        """
        params = args[0]  # Get first parameter dictionary
        parameter = VectorBacthQueryParameter(**params)
        return self.batch_query(parameter)
