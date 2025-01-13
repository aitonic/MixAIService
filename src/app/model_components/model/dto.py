from typing import Any, Optional

from pydantic import BaseModel, Field

from .constants import DEFAULT_EMBED_MODEL, DEFAULT_MAX_RETRIES


class BaseMessage(BaseModel):
    role: str = Field("user", pattern="user|assistant|system", description="角色")
    content: str | None = Field(default="")


class SystemMessage(BaseMessage):
    role: str = Field("system")


class UserMessage(BaseMessage):
    role: str = Field("user")


class AIMessage(BaseMessage):
    role: str | None = Field("assistant")


class CompletionsChoice(BaseModel):
    message: AIMessage | None = Field(default=None, description="非流式响应时候的消息")
    delta: AIMessage | None = Field(default=None, description="流式响应时候的消息")
    index: int = Field(default=0, description="索引")
    logprobs: float | None = Field(default=None, description="对数概率")
    finish_reason: str | None = Field(default=None, description="结束原因")


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
    api_key: str = None
    base_url: str = None
    full_url: Optional[str] = Field(default=None)
    max_retry: int = DEFAULT_MAX_RETRIES


class BaseCompletionParameter(BaseLLMParameter):
    messages: list[BaseMessage]
    temperature: float = 0.95
    max_new_tokens: int = 4096
    stream: bool = False
    model:str = "llama3pro"

class EmbedParameter(BaseModel):
    query: str 
    model: str = Field(default=DEFAULT_EMBED_MODEL)
    encoding_format: str = Field(default="float")

    def __init__(self, **data: dict[str, Any]) -> None:
        """初始化方法，接收动态的键值对数据。

        Args:
            **data (dict[str, Any]): 动态传入的键值对数据。

        """
        super().__init__(**data)
        # 检查并赋值参数
        self.query = data.get("query") or data.get("text") or data.get("input")
        self.model = data.get("model", DEFAULT_EMBED_MODEL)
        self.encoding_format = data.get("encoding_format", "float")
