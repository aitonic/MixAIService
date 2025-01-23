from datetime import datetime
from typing import Any

import httpx
import requests
from pydantic import BaseModel, Field

from src.utils.logger import logger

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
        cls: type["MixRequestModel"],  # 假设该方法属于类 MixModel
        model: str,
        messages: list[BaseMessage],
        parameter: MixParameter,
        stream: bool = False,
    ) -> "MixRequestModel":  # 返回当前类的实例
        """根据消息创建 MixRequestModel 的实例。

        Args:
            cls (Type[MixModel]): 类本身。
            model (str): 模型名称。
            messages (list[BaseMessage]): 消息列表。
            parameter (MixParameter): 混合参数配置。
            stream (bool, optional): 是否启用流式处理。默认为 False。

        Returns:
            MixRequestModel: MixRequestModel 的实例。

        """
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



    def validate_custom_rules(self) -> None:
        """实现自定义校验逻辑。

        Returns:
            None: 方法不返回任何值。

        """
    # 实现自定义校验逻辑
        pass

    def generate(self, parameter: BaseCompletionParameter) -> ModelResponse:  # type: ignore
        # 创建请求模型
        request_model = self.__build_request_model(
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
            """
            发送请求到 completion URL。

            Args:
                request_model: 包含请求数据的模型。

            Returns:
                Response: 请求的响应。
            """
            try:
                response = requests.post(
                    self.completion_url,
                    json=request_model.model_dump(),
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30  # 设置超时时间为 30 秒

                )
                response.raise_for_status()
                break
            except requests.Timeout:
                print("请求超时，请检查网络或服务状态")
                count = count + 1
            except requests.RequestException as e:
                # 处理请求异常
                logger.info(f"请求失败: {e}")
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
        request_model = self.__build_request_model(
            messages, temperature, max_new_tokens, model, stream
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.completion_url,
                json=request_model.model_dump(),
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

        request_model = MixRequestModel.from_messages(
            model=model if model else self.external_call_type,
            messages=messages,
            parameter=self.parameter,
            stream=stream,
        )

        return request_model


    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> ModelResponse:
        """调用模型完成操作。

        Args:
            *args: 包含一个参数字典的元组，通常为请求参数。
            **kwds: 可选的额外关键字参数。

        Returns:
            ModelResponse: 模型的响应对象。

        """
        param = args[0]
        return self.generate(BaseCompletionParameter(**param))
