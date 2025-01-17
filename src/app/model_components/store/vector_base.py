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
        """Create a ChromaVectorStore instance and return the client.

        Args:
            parameter (VectorParameter): Parameter object containing information required to create the client.

        Returns:
            bool: Indicates whether the client creation was successful.

        Raises:
            ValueError: If the parameter is invalid or client creation fails, an exception will be raised.

        """
        pass
    
    @abstractmethod
    def create_collection(self, collection_name:str) -> bool:
        """Method to create a collection, returns a boolean indicating success.

        Args:
            collection_name (str): Name of the collection to create.

        Returns:
            bool: Returns True if collection creation is successful, otherwise False.

        """
        pass

    @abstractmethod
    def add_text(self, parameter:VectorAddParameter) -> str:
        """Method to add text to the specified collection, returns a boolean indicating success.

        Args:
            parameter (VectorAddParameter): Parameter containing the text to be added, collection name, and embedding function.

        Returns:
            str: Returns the ID of the added text if successful, otherwise returns None.

        Raises:
            Exception: Will raise an exception if the collection does not exist.

        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name:str) -> bool:
        pass

    @abstractmethod
    def query(self, parameter: VectorQueryParameter) -> VectorRetriverResult:
        """Method to query the specified collection and return the query results.

        Args:
            parameter (VectorQueryParameter): Contains query parameters including query text, 
                collection name, and embedding function.

        Returns:
            VectorRetriverResult: Query results containing top 5 results related to the query text.

        Raises:
            Exception: Raises an exception if the specified collection does not exist.

        """
        pass

    # 生成唯一ID的方法，支持可选前缀
    def get_id(self, prefix: str = None) -> str:
        # Generate UUID with optional prefix
        uuid = identifier_util.generate_by_uuid()
        # If prefix is provided, return combination of prefix and UUID
        if prefix:
            return f"{prefix}-{uuid}"
        
        return uuid  # Return generated UUID
    
    def batch_query(self, parameter: VectorBacthQueryParameter) -> list[VectorRetriverResult]:
        
        result = []
        for col in parameter.search_collections:
            try:
                result.append(self.query(VectorQueryParameter(query_text=parameter.query_text, 
                                                          collection_name=col, 
                                                          embed_function=parameter.embed_function,
                                                          result_count=parameter.result_count)))
            except Exception as e:
                logger.error(f"Error retrieving data from collection:{col}: error info{traceback.format_exc()}")
        
        return result
            
