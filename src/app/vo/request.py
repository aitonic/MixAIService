
from pydantic import BaseModel, Field


class RunData(BaseModel):
    query: str = Field(description="Input data for the request")
    base_url: str | None = Field(default=None, description="Base URL for the model (completions/embeddings), e.g. http://127.0.0.1:1234")
    full_url: str | None = Field(default=None, description="Full URL for the model (completions/embeddings), required when not using OpenAI format URL")
    system_prompt: str | None = Field(default=None, description="System message content")
    search_collections: list[str] | None = Field(default=None, description="Collections to search when performing vector retrieval")
    collection_name: str | None = Field(default=None, description="Collection name when adding text to vector storage")
    result_count: int | None = Field(default=5, description="Number of records to return when performing vector search")

    class Config:
        """Specify additional model options by this Configuration class.

        Attributes:
            extra (str): Specifies whether the model allows extra fields. 
                         Value "allow" means extra fields are allowed.
        """
        extra = "allow"


class RunParameter(BaseModel):
    app_no: str = Field(alias="appNo")
    data: RunData = Field(description="Execution parameters that will be applied when executing components")
