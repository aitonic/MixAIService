import os
from collections.abc import AsyncGenerator, Iterator

import httpx
from pydantic import BaseModel, Field

from src.utils.exceptions import LLMAPIError, LLMAuthorizationError, LLMTimeoutError
from src.utils.logger import logger

from .base import AbsLLMModel
from .constants import (
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_REPETITION_PENALTY,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_N,
    DEFAULT_TOP_P,
)
from .dto import BaseCompletionParameter, BaseLLMParameter, BaseMessage, ModelResponse


class RequestModel(BaseModel):
    model: str
    messages: list[dict]
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS
    temperature: float = DEFAULT_TEMPERATURE
    stop: str | None = Field(default="。")
    stream: bool = False

    @classmethod
    def from_messages(
        cls: type["RequestModel"],  # 指定 cls 的类型为当前类
        model: str,
        messages: list[BaseMessage],
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        stop: list[str] | None = None,
        stream: bool = False,
    ) -> "RequestModel":  # 返回值类型为当前类
        """Create a RequestModel instance from messages.

        Args:
            model (str): Model name.
            messages (List[BaseMessage]): List of messages.
            max_new_tokens (int): Maximum number of tokens to generate.
            temperature (float): Generation temperature.
            stop (Optional[List[str]]): Stop words.
            stream (bool): Whether to enable streaming generation.

        Returns:
            RequestModel: Instance of current class.

        """
        messages_dict = [message.model_dump() for message in messages]
        return cls(
            model=model,
            messages=messages_dict,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            stop=stop,
            stream=stream,
        )


class OpenAiStyleLLMParameter(BaseLLMParameter):
    top_p: float = Field(default=DEFAULT_TOP_P)
    top_n: int = Field(default=DEFAULT_TOP_N)
    repetition_penalty: float = Field(default=DEFAULT_REPETITION_PENALTY)
    embed_model: str = os.getenv("EMBEDDING_MODEL_NAME")


# 一个类似与openai的模型类，但是可以定义自己的校验
class OpenAiStyleModel(AbsLLMModel):
    def __init__(self, parameter: OpenAiStyleLLMParameter) -> None:
        super().__init__(parameter)
        self.top_p = parameter.top_p
        self.top_n = parameter.top_n
        self.repetition_penalty = parameter.repetition_penalty
        self.full_url = parameter.full_url
        self.base_url = parameter.base_url
        self.embed_model = parameter.embed_model

        self.validate_custom_rules()

    def validate_custom_rules(self) -> None:
        """Implement custom validation logic.

        This method validates custom rules, where api_key is allowed to be empty.
        """
        pass

    def generate(self, parameter: BaseCompletionParameter) -> Iterator[ModelResponse]:
        """非流式生成。"""
        try:
            yield from self.completions.create(parameter)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred during LLM call: {e}")
            # Handle specific HTTP errors, e.g., retry for timeouts, raise custom exceptions
            if isinstance(e, httpx.TimeoutException):
                raise LLMTimeoutError("LLM API call timed out.") from e
            elif e.response.status_code == 401:
                raise LLMAuthorizationError("Unauthorized access to LLM API.") from e
            else:
                raise LLMAPIError(f"LLM API request failed with status code: {e.response.status_code}") from e

    
    async def async_generate(self, parameter: BaseCompletionParameter) -> AsyncGenerator[ModelResponse, None]:
        """Send POST request and get response, supports streaming output.
        
        Args:
            parameter (BaseCompletionParameter): The completion parameters containing messages and settings
        
        Returns:
            AsyncGenerator[ModelResponse, None]: An async generator yielding ModelResponse objects

        """
        count = 0
        for count, response in enumerate(self.completions.create(parameter), start=1):
            yield response
            if count >= parameter.max_new_tokens:
                break


    async def async_completion(
        self,
        parameter: BaseCompletionParameter
    ) -> AsyncGenerator[ModelResponse, None]:
        # 创建请求模型
        request_model = self.__build_request_model(
            parameter.messages, parameter.temperature, parameter.max_new_tokens, parameter.stream
        )

        async with httpx.AsyncClient() as client, client.post(
            self.completion_url,
            json=request_model.model_dump(),
            headers={"Authorization": f"Bearer {self.api_key}"},
        ) as response:
                async for line in response.aiter_lines():
                    if line:
                        yield line  # 逐行输出结果


    def __build_request_model(
        self,
        messages: list[BaseMessage],
        temperature: float = None,
        max_new_tokens: int = None,
        stream: bool = False,
    ) -> RequestModel:  # type: ignore
        # 创建请求模型
        request_model = RequestModel.from_messages(
            model=self.model,
            messages=messages,
            max_new_tokens=max_new_tokens if max_new_tokens else self.max_new_tokens,
            temperature=temperature if temperature else self.temperature,
            stream=stream,
        )

        logger.info(f"Built model request parameters: {request_model.model_dump()}")
        return request_model
