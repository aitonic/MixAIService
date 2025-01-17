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
        """Get the URL for completion request.

        Returns:
            str: The complete URL.

        """
        if self.full_url:
            return self.full_url
        return self.base_url + DEFAULT_COMPLETION_PATH
    
    def create(self, parameter: BaseCompletionParameter) -> Iterator[ModelResponse]:
         count = 0
         with httpx.Client(timeout=300) as client:
            while count < self.max_retry:
                try:
                    request_json = {
                            "messages":[message.model_dump() for message in parameter.messages],
                            "temperature":parameter.temperature,
                            "stream":parameter.stream,
                            "max_new_tokens":parameter.max_new_tokens,
                            "model":parameter.model
                        }
                    logger.info(f"LLM invoke parameters：{request_json}")
                    response = client.post(
                        self.completion_url,
                        json=request_json,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                    )
                    response.raise_for_status()

                    if not parameter.stream:
                        # 非流式处理
                        data = response.json()
                        if not data.get("choices") or len(data["choices"]) == 0:
                            raise ValueError(f"Invalid API response: {data}")
                        result = ModelResponse(**data)
                        yield result
                    else:
                        # 流式处理
                        for line in response.iter_lines():
                            if not line:
                                continue
                            if "DONE" in line:
                                break
                            try:
                                # 解析流式数据
                                json_data = json.loads(line.replace("data:", ""))
                                if "choices" in json_data and len(json_data["choices"]) > 0:
                                    yield ModelResponse(**json_data)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse stream data: {line}")
                                continue
                except Exception as e:
                    logger.error(f"completions接口出错：{traceback.format_exc()}")
                    count += 1
                    if count >= self.max_retry:
                        raise RuntimeError(f"Max retries ({self.max_retry}) exceeded") from e
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
        """Abstract method to define specific generation logic.

        Args:
            parameter (BaseCompletionParameter): Parameter object required for generation.

        Raises:
            Exception: If the subclass does not implement this method, this exception will be raised.

        """
        raise Exception("Unimplemented generation method")
    
    @abstractmethod
    async def async_generate(self, parameter: BaseCompletionParameter) -> AsyncGenerator[ModelResponse, None]:
        """Abstract method to define specific generation logic.

        Args:
            parameter (BaseCompletionParameter): Parameter object required for generation.

        Raises:
            Exception: If the subclass does not implement this method, this exception will be raised.

        """
        raise Exception("Unimplemented generation method")

    # @abstractmethod
    def after_response(self, response: ModelResponse) -> None:
        """Operations to perform after model response.

        Args:
            response (ModelResponse): model response object

        """
        logger.info(f"Processing response: {response}")
        

    def __call__(self, *args: tuple[dict[str, Any], ...], **kwds: dict[str, Any]) -> Iterator[ModelResponse]:
        """Call method for model generation.

        Args:
            *args (tuple[dict[str, Any], ...]): Positional arguments containing parameters
            **kwds (dict[str, Any]): Keyword arguments containing parameters

        Returns:
            Iterator[ModelResponse]: Iterator yielding model response content

        """
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

