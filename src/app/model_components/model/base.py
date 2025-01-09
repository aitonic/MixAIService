import json
import os
import traceback
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Iterator
from typing import Any

import httpx

from src.utils.logger import logger

from ..base_component import BaseComponent
from .constants import (
    DEFAULT_COMPLETION_PATH,
    DEFAULT_EMBEDDING_PATH,
)
from .dto import (
    BaseCompletionParameter,
    BaseLLMParameter,
    ModelResponse,
)
from .embedding import OpenAiStyleEmbeddings


class Completions:
    suffix = DEFAULT_COMPLETION_PATH

    def __init__(self, api_key: str = None,
                        base_url: str = None,
                        full_url: str = None,
                        max_retry: int = 3) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.full_url = full_url
        self.max_retry = max_retry

    @property
    def completion_url(self) -> str:
        """获取完成请求的 URL。

        Returns:
            str: 完整的 URL。

        """
        if self.full_url:
            return self.full_url
        return self.base_url + DEFAULT_COMPLETION_PATH
    
    def create(self, parameter: BaseCompletionParameter) -> Iterator[ModelResponse]:
         count = 0
         with httpx.Client(timeout=30) as client:
            while count < self.max_retry:
                try:
                    response = client.post(
                        self.completion_url,
                        json={
                            "messages":[message.model_dump() for message in parameter.messages],
                            "temperature":parameter.temperature,
                            "stream":parameter.stream,
                            "max_new_tokens":parameter.max_new_tokens,
                            "model":parameter.model
                        },
                        headers={"Authorization": f"Bearer {self.api_key}"},
                    )
                    response.raise_for_status()

                    # data = response.json()  # 获取响应的 JSON 数据
                    if not parameter.stream:
                        # 如果不使用流式返回
                        data = response.json()  # 获取响应的 JSON 数据

                        if not data.get("choices") or len(data["choices"]) == 0:
                            raise ValueError(f"Invalid API response: {data}")

                        result = ModelResponse(**data)  # 将响应数据映射到模型

                        # yield result.choices[0].message.content
                        yield result
                    # 使用流式返回
                    for line in response.iter_lines():
                        if line:
                            if "DONE" in line:
                                return
                            # 去掉 'data:' 前缀并解析 JSON 数据
                            data = json.loads(line.replace("data:", ""))
                            result = ModelResponse(**data)
                            yield result
                except Exception:
                    logger.error(f"completions接口出错：{traceback.format_exc()}")
                    count = count+1
            # 如果不使用流式返回
            
            # result = MixResponse(**data)  # 将响应数据映射到模型
            # yield result.choices[0].message.content

class AbsLLMModel(ABC, BaseComponent):
    api_key: str = None
    base_url: str = None
    full_url: str = None
    max_retry: int = 3

    def __init__(self, parameter: BaseLLMParameter) -> None:
        # if isinstance(parameter, dict):
        #     parameter = BaseLLMParameter(**parameter)
        api_key = parameter.api_key
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.api_key = api_key
        self.base_url = parameter.base_url
        self.full_url = parameter.full_url
        self.max_retry = parameter.max_retry

    @property
    def completion_url(self) -> str:
        if self.full_url:
            return self.full_url
        return self.base_url + DEFAULT_COMPLETION_PATH
    
    @property
    def embed_url(self) -> str:
        if self.full_url:
            return self.full_url
        return self.base_url + DEFAULT_EMBEDDING_PATH
    
    @property
    def chat(self) -> "AbsLLMModel":
        return self
    
    @property
    def completions(self) -> Completions:
        return Completions(api_key=self.api_key, base_url=self.base_url, full_url=self.full_url, max_retry=self.max_retry)
    
    @property
    def embeddings(self) -> OpenAiStyleEmbeddings:
        return OpenAiStyleEmbeddings(
            BaseLLMParameter(
                api_key=self.api_key,
                base_url=self.base_url,
                full_url=self.full_url,
                max_retry=self.max_retry
            )
        )

    @abstractmethod
    def generate(self, parameter: BaseCompletionParameter) -> ModelResponse:
        """抽象方法，用于定义具体的生成逻辑。

        参数:
            parameter (BaseCompletionParameter): 生成所需的参数对象。

        异常:
            Exception: 如果子类未实现该方法，将引发此异常。

        """
        raise Exception("未实现的生成方法")
    
    @abstractmethod
    async def async_generate(self, parameter: BaseCompletionParameter) -> AsyncGenerator[ModelResponse, None]:
        """抽象方法，用于定义具体的生成逻辑。

        参数:
            parameter (BaseCompletionParameter): 生成所需的参数对象。

        异常:
            Exception: 如果子类未实现该方法，将引发此异常。

        """
        raise Exception("未实现的生成方法")

    # @abstractmethod
    def after_response(self, response: ModelResponse) -> None:
        """在模型响应后执行的操作。

        Args:
            response (ModelResponse): 模型的响应对象。

        """
        logger.info(f"Processing response: {response}")
        

    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> Iterator[ModelResponse]:

        param = args[0]
        parameter = BaseCompletionParameter(**param)
        if parameter.stream:
            # 流式
            result = self.generate(parameter)
            for r in result:
                yield r.choices[0].message.content
        else:
            # 同步调用
            result = self.generate(parameter)
            for r in result:
                self.after_response(r)
                yield r.choices[0].message.content

