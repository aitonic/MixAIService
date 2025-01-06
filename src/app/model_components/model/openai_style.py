import json
from collections.abc import AsyncGenerator, Iterator
from typing import Any

import httpx
import requests
from pydantic import BaseModel, Field

from .base import AbsLLMModel
from .constants import (
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_MODEL,
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
        cls,
        model: str,
        messages: list[BaseMessage],
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        stop: list[str] | None = None,
        stream: bool = False,
    ):
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
    model: str = Field(default=DEFAULT_MODEL)
    max_new_tokens: int = Field(default=DEFAULT_MAX_NEW_TOKENS)
    temperature: float = Field(default=DEFAULT_TEMPERATURE)
    top_p: float = Field(default=DEFAULT_TOP_P)
    top_n: int = Field(default=DEFAULT_TOP_N)
    repetition_penalty: float = Field(default=DEFAULT_REPETITION_PENALTY)


# 一个类似与openai的模型类，但是可以定义自己的校验
class OpenAiStyleModel(AbsLLMModel):
    def __init__(self, parameter: OpenAiStyleLLMParameter) -> None:
        super().__init__(parameter)
        self.temperature = parameter.temperature
        self.top_p = parameter.top_p
        self.top_n = parameter.top_n
        self.repetition_penalty = parameter.repetition_penalty
        self.max_new_tokens = parameter.max_new_tokens
        self.full_url = parameter.full_url
        self.base_url = parameter.base_url
        self.model = parameter.model

        self.validate_custom_rules()

    def validate_custom_rules(self):
        # 实现自定义校验逻辑
        # api_key允许为空
        pass

    def completion(self, parameter: BaseCompletionParameter) -> Iterator[ModelResponse]:
        # 创建请求模型
        requestModel = self.__build_request_model(
            parameter.messages,
            parameter.temperature,
            parameter.max_new_tokens,
            parameter.stream,
        )

        # 发送 POST 请求，获取响应
        count = 0
        while count < self.max_retry:
            # print(f"count:{str(count)}")
            try:
                response = requests.post(
                    self.completion_url,
                    json=requestModel.model_dump(),
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                break
            except requests.RequestException as e:
                # 处理请求异常
                print(f"请求失败: {e}")
                count = count + 1

        if not parameter.stream:
            # 如果不使用流式返回
            data = response.json()  # 获取响应的 JSON 数据

            if not data.get("choices") or len(data["choices"]) == 0:
                raise ValueError(f"Invalid API response: {data}")

            result = ModelResponse(**data)  # 将响应数据映射到模型

            yield result.choices[0].message.content
        # 使用流式返回
        for line in response.iter_lines():
            if line:
                # print(line.decode('utf-8'))
                if "DONE" in line.decode("utf-8"):
                    return
                # 去掉 'data:' 前缀并解析 JSON 数据
                data = json.loads(line.decode("utf-8").replace("data:", ""))
                result = ModelResponse(**data)
                yield result.choices[0].delta.content

    async def async_completion(
        self,
        messages: list[BaseMessage],
        temperature: float = None,
        max_new_tokens: int = None,
        stream: bool = False,
    ) -> AsyncGenerator[ModelResponse, None]:
        # 创建请求模型
        requestModel = self.__build_request_model(
            messages, temperature, max_new_tokens, stream
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.completion_url,
                json=requestModel.model_dump(),
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()

            if not stream:
                # 如果不使用流式返回
                data = response.json()  # 获取响应的 JSON 数据
                result = ModelResponse(**data)  # 将响应数据映射到模型
                yield result.choices[0].message.content
            else:
                # 使用流式返回
                async for line in response.aiter_lines():
                    if line:
                        if "DONE" in line.decode("utf-8"):
                            return
                        # 去掉 'data:' 前缀并解析 JSON 数据
                        data = json.loads(line.decode("utf-8").replace("data:", ""))
                        result = ModelResponse(**data)
                        yield result.choices[0].delta.content

    def __build_request_model(
        self,
        messages: list[BaseMessage],
        temperature: float = None,
        max_new_tokens: int = None,
        stream: bool = False,
    ) -> ModelResponse:  # type: ignore
        # 创建请求模型
        return RequestModel.from_messages(
            model=self.model,
            messages=messages,
            max_new_tokens=max_new_tokens if max_new_tokens else self.max_new_tokens,
            temperature=temperature if temperature else self.temperature,
            stream=stream,
        )

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        param = args[0]
        return self.completion(BaseCompletionParameter(**param))
