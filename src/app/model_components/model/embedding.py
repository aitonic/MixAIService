from typing import Any
from .dto import (
    BaseLLMParameter, 
    EmbedParameter
)
from .constants import (
    DEFAULT_EMBEDDING_PATH,
)

class OpenAiStyleEmbeddings:
    """
    The OpenAiStyleEmbeddings class is designed to interact with the OpenAI embedding API. 
    This class provides a method to create embeddings, allowing users to input text and receive 
    the corresponding embedding results. Users can specify the embedding model and encoding format to be used.
    """
    suffix = DEFAULT_EMBEDDING_PATH

    def __init__(self, parameter: BaseLLMParameter) -> None:
        self.api_key = parameter.api_key
        self.base_url = parameter.base_url
        self.full_url = parameter.full_url
        self.max_retry = parameter.max_retry

    @property
    def embed_url(self) -> str:
        if self.full_url:
            return self.full_url
        return self.base_url + DEFAULT_EMBEDDING_PATH
    
    def create(self, parameter:EmbedParameter) -> dict:
        """Method to call the embedding interface, with input and output parameters consistent with the OpenAI interface.

        Args:
            text (str): Input text.
            model (str): The embedding model to use, default is DEFAULT_EMBED_MODEL.
            encoding_format (str): The encoding format, default is "float".

        Returns:
            dict: The return value of the embedding interface call, containing the embedding results.

        """
        url = self.embed_url
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "input": parameter.query,
            "model": parameter.model,
            "encoding_format": parameter.encoding_format
        }
        
        import httpx

        with httpx.Client(timeout=30) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.create(EmbedParameter(**args[0]))