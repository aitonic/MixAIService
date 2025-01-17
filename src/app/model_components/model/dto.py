import os
from typing import Any

from pydantic import BaseModel, Field

from .constants import DEFAULT_EMBED_MODEL, DEFAULT_MAX_RETRIES


class BaseMessage(BaseModel):
    role: str = Field("user", pattern="user|assistant|system", description="content role")
    content: str | None = Field(default="")


class SystemMessage(BaseMessage):
    role: str = Field("system")


class UserMessage(BaseMessage):
    role: str = Field("user")


class AIMessage(BaseMessage):
    role: str | None = Field("assistant")


class CompletionsChoice(BaseModel):
    """Represents a choice in the completions response.

    Attributes:
        message: The message for non-streaming responses
        delta: The message for streaming responses
        index: The index of the choice
        logprobs: The log probabilities of the tokens
        finish_reason: The reason why the response finished

    """

    message: AIMessage | None = Field(default=None, description="Message for non-streaming responses")
    delta: AIMessage | None = Field(default=None, description="Message for streaming responses")
    index: int = Field(default=0, description="Index of the choice")
    logprobs: float | None = Field(default=None, description="Log probabilities of the tokens")
    finish_reason: str | None = Field(default=None, description="Reason for finishing the response")


class ModelResponse(BaseModel):
    id: str = Field(default=None, description="id")
    object: str = Field(
        default="chat.completions",
        description="object:chat.completions|chat.completions.chunk",
    )
    created: int = Field(default=None, description="创建时间")
    choices: list[CompletionsChoice] = Field(default=[], description="消息列表")
    usage: dict | None = Field(default=None, description="usage")
    model: str = Field(default="MIX", description="模型")
    system_fingerprint: str = Field(default="MIX", description="系统指纹")


class BaseLLMParameter(BaseModel):
    api_key: str | None  = os.getenv("MODEL_API_KEY")
    base_url: str | None  = os.getenv("MODEL_BASE_URL")
    full_url: str | None = Field(default=None)
    max_retry: int = DEFAULT_MAX_RETRIES


class BaseCompletionParameter(BaseLLMParameter):
    messages: list[BaseMessage]
    temperature: float = 0.95
    max_new_tokens: int = os.getenv("MODEL_MAX_TOKENS")
    stream: bool = False
    model:str = os.getenv("CHAT_MODEL_NAME")

class EmbedParameter(BaseModel):
    query: str 
    model: str = os.getenv("EMBEDDING_MODEL_NAME")
    encoding_format: str = Field(default="float")

    def __init__(self, **data: dict[str, Any]) -> None:
        """Initialize the instance with dynamic key-value pairs.

        Args:
            **data (dict[str, Any]): Dynamic key-value pairs data.

        """
        super().__init__(**data)
        # 检查并赋值参数
        self.query = data.get("query") or data.get("text") or data.get("input")
        self.model = data.get("model", DEFAULT_EMBED_MODEL)
        self.encoding_format = data.get("encoding_format", "float")
