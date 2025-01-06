from datetime import datetime
from typing import Any

import httpx
import requests
from pydantic import BaseModel, Field

from .base import AbsLLMModel
from .constants import (
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_REPETITION_PENALTY,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_N,
    DEFAULT_TOP_P,
)
from .dto import (
    AIMessage,
    BaseCompletionParameter,
    BaseLLMParameter,
    BaseMessage,
    CompletionsChoice,
    ModelResponse,
)

DEFAULT_MODEL = "llama3pro"
COMPLETION_PATH = "/v1/chat/completions"
MODEL_PATH = "/v1/models"
EMBEDDING_PATH = "/v1/embeddings"


class MixResponse(BaseModel):
    Response: str
    Response_wm: str
    prompt_tokens: float
    completion_tokens: float
    total_tokens: float


class MixParameter(BaseModel):
    max_new_tokens: int = (DEFAULT_MAX_NEW_TOKENS,)
    temperature: float = (DEFAULT_TEMPERATURE,)
    top_p: float = (0.95,)
    top_n: int = (50,)
    repetition_penalty: float = 1.1


class MixRequestModel(BaseModel):
    external_call_type: str
    messages: list[dict]
    parameter: MixParameter
    stream: bool = False

    @classmethod
    def from_messages(
        cls,
        model: str,
        messages: list[BaseMessage],
        parameter: MixParameter,
        stream: bool = False,
    ):
        messages_dict = [message.model_dump() for message in messages]
        return cls(
            external_call_type=model,
            messages=messages_dict,
            parameter=parameter,
            stream=stream,
        )


class MixLLMParameter(BaseLLMParameter):
    model: str = (Field(default=DEFAULT_MODEL),)
    max_new_tokens: int = Field(default=DEFAULT_MAX_NEW_TOKENS, description="最大token")
    temperature: float = (Field(default=DEFAULT_TEMPERATURE),)
    top_p: float = (Field(default=DEFAULT_TOP_P),)
    top_n: int = (Field(default=DEFAULT_TOP_N),)
    repetition_penalty: float = Field(default=DEFAULT_REPETITION_PENALTY)


# 一个类似与openai的模型类，但是可以定义自己的校验
class Mix(AbsLLMModel):
    parameter: MixParameter
    external_call_type: str = DEFAULT_MODEL

    def __init__(self, parameter: MixLLMParameter) -> None:
        # parameter = MixLLMParameter(**parameter.model_dump())
        super().__init__(parameter)
        self.parameter = MixParameter(**parameter.model_dump())
        self.full_url = parameter.full_url
        self.base_url = parameter.base_url
        self.external_call_type = parameter.model

        self.validate_custom_rules()

    def validate_custom_rules(self):
        # 实现自定义校验逻辑
        pass

    def completion(self, parameter: BaseCompletionParameter) -> ModelResponse:  # type: ignore
        # 创建请求模型
        requestModel = self.__build_request_model(
            parameter.messages,
            parameter.temperature,
            parameter.max_new_tokens,
            parameter.model,
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

        if parameter.stream:
            raise Exception("stream is not supported in mix")

        # 如果不使用流式返回
        data = response.json()  # 获取响应的 JSON 数据
        result = MixResponse(**data)  # 将响应数据映射到模型
        return ModelResponse(
            id="",
            object="chat.completions",
            created=int(datetime.now().timestamp() * 1000),
            choices=[
                CompletionsChoice(
                    message=AIMessage(content=result.Response),
                    index=0,
                    logprobs=None,
                    finish_reason="stop",
                )
            ],
            usage=result.model_dump(),
            model="MIX",
            system_fingerprint="MIX",
        )

    async def async_completion(
        self,
        messages: list[BaseMessage],
        temperature: float = None,
        max_new_tokens: int = None,
        model: str = None,
        stream: bool = False,
    ) -> ModelResponse:  # type: ignore
        # 创建请求模型
        requestModel = self.__build_request_model(
            messages, temperature, max_new_tokens, model, stream
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.completion_url,
                json=requestModel.model_dump(),
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()

            # 如果不使用流式返回
            data = response.json()  # 获取响应的 JSON 数据
            result = MixResponse(**data)  # 将响应数据映射到模型
            yield result.choices[0].message.content

    def __build_request_model(
        self,
        messages: list[BaseMessage],
        temperature: float = None,
        max_new_tokens: int = None,
        model: str = None,
        stream: bool = False,
    ) -> ModelResponse:  # type: ignore
        # 创建请求模型
        # 创建请求模型
        parameter = self.parameter
        if temperature:
            parameter.temperature = temperature

        if max_new_tokens:
            parameter.max_new_tokens = max_new_tokens

        requestModel = MixRequestModel.from_messages(
            model=model if model else self.external_call_type,
            messages=messages,
            parameter=self.parameter,
            stream=stream,
        )

        return requestModel

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        param = args[0]
        return self.completion(BaseCompletionParameter(**param))


# client = MIX(base_url="192.168.6.16:8070", api_key="1234", full_url="http://192.168.6.16:8070/generate/")
# # 非流式
# result = client.completion(messages=[SystemMessage(content="你是一个小助手，你的名字是小马。"),UserMessage(content="介绍一下你自己")], stream=False)
# print(result.model_dump())
