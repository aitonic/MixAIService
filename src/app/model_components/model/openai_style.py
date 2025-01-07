import json
from collections.abc import AsyncGenerator, Iterator
from typing import Any

import httpx
import requests
from pydantic import BaseModel, Field

from src.utils.logger import logger

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
        cls: type["RequestModel"],  # 指定 cls 的类型为当前类
        model: str,
        messages: list[BaseMessage],
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        stop: list[str] | None = None,
        stream: bool = False,
    ) -> "RequestModel":  # 返回值类型为当前类
        """根据消息创建 RequestModel 的实例。

        Args:
            model (str): 模型名称。
            messages (List[BaseMessage]): 消息列表。
            max_new_tokens (int): 最大生成的 token 数量。
            temperature (float): 生成温度。
            stop (Optional[List[str]]): 停止词。
            stream (bool): 是否启用流式生成。

        Returns:
            RequestModel: 当前类的实例。

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

    def validate_custom_rules(self) -> None:
        """实现自定义校验逻辑。

        当前方法会校验自定义规则，其中 api_key 允许为空。
        """
        # 实现自定义校验逻辑
        # api_key允许为空
        pass

    def completion(self, parameter: BaseCompletionParameter) -> Iterator[ModelResponse]:
        # 创建请求模型
        request_model = self.__build_request_model(
            parameter.messages,
            parameter.temperature,
            parameter.max_new_tokens,
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
        request_model = self.__build_request_model(
            messages, temperature, max_new_tokens, stream
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.completion_url,
                json=request_model.model_dump(),
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
        request_model = RequestModel.from_messages(
            model=self.model,
            messages=messages,
            max_new_tokens=max_new_tokens if max_new_tokens else self.max_new_tokens,
            temperature=temperature if temperature else self.temperature,
            stream=stream,
        )

        logger.info(f"构建的模型请求参数：{request_model.model_dump()}")
        return request_model

    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> ModelResponse:

        param = args[0]
        return self.completion(BaseCompletionParameter(**param))
