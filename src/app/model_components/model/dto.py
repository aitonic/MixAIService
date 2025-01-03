from pydantic import BaseModel, Field
import os
from typing import Optional, List

from .constants import DEFAULT_MAX_RETRIES

class BaseMessage(BaseModel):
    role:str = Field("user", pattern="user|assistant|system", description="角色")
    content:Optional[str] = Field(default="")

class SystemMessage(BaseMessage):
    role:str = Field("system")

class UserMessage(BaseMessage):
    role:str = Field("user")

class AIMessage(BaseMessage):
    role:Optional[str] = Field("assistant")

class CompletionsChoice(BaseModel):
    message:Optional[AIMessage] = Field(default=None, description="非流式响应时候的消息")
    delta:Optional[AIMessage] = Field(default=None, description="流式响应时候的消息")
    index:int = Field(default=0, description="索引")
    logprobs:Optional[float] = Field(default=None, description="对数概率")
    finish_reason:Optional[str] = Field(default=None, description="结束原因")

class ModelResponse(BaseModel):
    id:str = Field(default=None, description="id")
    object:str = Field(default="chat.completions", description="object:chat.completions|chat.completions.chunk")
    created:int = Field(default=None, description="创建时间")
    choices:list[CompletionsChoice] = Field(default=[], description="消息列表")
    usage:Optional[dict] = Field(default=None, description="usage")
    model:str = Field(default="MIX", description="模型")
    system_fingerprint:str = Field(default="MIX", description="系统指纹")

class BaseLLMParameter(BaseModel):
    api_key:str = None
    base_url:str = None
    full_url:str = None
    max_retry:int = DEFAULT_MAX_RETRIES

class BaseCompletionParameter(BaseLLMParameter):
    messages: List[BaseMessage]
    temperature: float = None 
    max_new_tokens: int = None
    stream: bool = False