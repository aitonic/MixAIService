from typing import Any
from .dto import (
    EmbedParameter,
    BaseLLMParameter
)
from .constants import (
    DEFAULT_EMBEDDING_PATH,
)
from ..base_component import BaseComponent

class OpenAiStyleEmbeddings(BaseComponent):
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
        """Call the embedding interface, ensuring input and output parameters are consistent with the OpenAI interface.

        Args:
            text (str): Input text.
            model (str): The embedding model to use, default is DEFAULT_EMBED_MODEL.
            encoding_format (str): The encoding format, default is "float".
            parameter (EmbedParameter): An object containing the input query, model, and encoding format.


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
            return response.json()["data"]

    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> dict:
        """Call the embedding interface with the provided parameters.

        Args:
            *args (tuple[dict[str, Any], ...]): Positional arguments containing a dictionary
                of parameters to initialize EmbedParameter.
            **kwds (dict[str, Any]): Keyword arguments (unused in this method).

        Returns:
            dict: The result of the embedding interface call.

        """
        return self.create(EmbedParameter(**args[0]))
    

class ChromaAdaptEmbeddings(OpenAiStyleEmbeddings):
    """
    The OpenAiStyleEmbeddings class is designed to interact with the OpenAI embedding API. 
    This class provides a method to create embeddings, allowing users to input text and receive 
    the corresponding embedding results. Users can specify the embedding model and encoding format to be used.
    """
   
    def __call__(self, input:list[str]) -> Any:
        return self.create(EmbedParameter({"query":input[0]}))