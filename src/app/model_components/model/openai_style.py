from collections.abc import AsyncGenerator

import httpx
from pydantic import BaseModel, Field

from src.utils.logger import logger

from .base import AbsLLMModel
from .constants import (
    DEFAULT_EMBED_MODEL,
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
    # model: str = Field(default=DEFAULT_MODEL)
    # max_new_tokens: int = Field(default=DEFAULT_MAX_NEW_TOKENS)
    # temperature: float = Field(default=DEFAULT_TEMPERATURE)
    top_p: float = Field(default=DEFAULT_TOP_P)
    top_n: int = Field(default=DEFAULT_TOP_N)
    repetition_penalty: float = Field(default=DEFAULT_REPETITION_PENALTY)
    embed_model: str = Field(default=DEFAULT_EMBED_MODEL)


# 一个类似与openai的模型类，但是可以定义自己的校验
class OpenAiStyleModel(AbsLLMModel):
    def __init__(self, parameter: OpenAiStyleLLMParameter) -> None:
        super().__init__(parameter)
        # self.temperature = parameter.temperature
        self.top_p = parameter.top_p
        self.top_n = parameter.top_n
        self.repetition_penalty = parameter.repetition_penalty
        # self.max_new_tokens = parameter.max_new_tokens
        self.full_url = parameter.full_url
        self.base_url = parameter.base_url
        # self.model = parameter.model
        self.embed_model = parameter.embed_model

        self.validate_custom_rules()

    def validate_custom_rules(self) -> None:
        """Implement custom validation logic.

        This method validates custom rules, where api_key is allowed to be empty.
        """
        # 实现自定义校验逻辑
        # api_key允许为空
        pass

    def generate(self, parameter: BaseCompletionParameter) -> ModelResponse:
        """非流式生成。"""
        return self.completions.create(parameter)

    
    async def async_generate(self, parameter: BaseCompletionParameter) -> AsyncGenerator[ModelResponse, None]:
        # 发送 POST 请求，获取响应，支持流式输出
        count = 0
        for count, response in enumerate(self.completions.create(parameter), start=1):
            yield response
            if count >= parameter.max_new_tokens:  # 根据需要限制输出数量
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

        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         self.completion_url,
        #         json=request_model.model_dump(),
        #         headers={"Authorization": f"Bearer {self.api_key}"},
        #     )
        #     response.raise_for_status()

        #     if not parameter.stream:
        #         # 如果不使用流式返回
        #         data = response.json()  # 获取响应的 JSON 数据
        #         result = ModelResponse(**data)  # 将响应数据映射到模型
        #         yield result.choices[0].message.content
        #     else:
        #         # 使用流式返回
        #         async for line in response.aiter_lines():
        #             if line:
        #                 if "DONE" in line.decode("utf-8"):
        #                     return
        #                 # 去掉 'data:' 前缀并解析 JSON 数据
        #                 data = json.loads(line.decode("utf-8").replace("data:", ""))
        #                 result = ModelResponse(**data)
        #                 yield result.choices[0].delta.content

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

    # def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> Iterator[ModelResponse]:

    #     param = args[0]
    #     return self.generate(BaseCompletionParameter(**param))
