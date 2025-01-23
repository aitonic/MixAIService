import json
import os
import traceback
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Iterator
from typing import Any

import httpx
import tiktoken

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

# 初始化 tiktoken 编码器
encoding = tiktoken.encoding_for_model("gpt-4")

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

    # Helper methods
    def _prepare_request(self, parameter: BaseCompletionParameter) -> dict:
        """Prepare the JSON payload for the completion request.

        Args:
            parameter (BaseCompletionParameter): The completion parameters.

        Returns:
            dict: The request payload.

        """
        return {
            "messages": [message.model_dump() for message in parameter.messages],
            "temperature": parameter.temperature,
            "stream": parameter.stream,
            "max_new_tokens": parameter.max_new_tokens,
            "model": parameter.model,
        }

    def _handle_non_stream_response(self, response: httpx.Response) -> Iterator[ModelResponse]:
        """Handle the response for non-streaming requests.

        Args:
            response (httpx.Response): The HTTP response.

        Returns:
            Iterator[ModelResponse]: Parsed model responses.

        """
        data = response.json()
        if not data.get("choices") or len(data["choices"]) == 0:
            raise ValueError(f"Invalid API response: {data}")
        yield ModelResponse(**data)

    def _handle_stream_response(self, response: httpx.Response) -> Iterator[ModelResponse]:
        """Handle the response for streaming requests.

        Args:
            response (httpx.Response): The HTTP response.

        Returns:
            Iterator[ModelResponse]: Parsed model responses from the stream.

        """
        # 逐块读取流式响应
        for line in response.iter_text():
            if not line:
                continue
            if "DONE" in line:
                yield "DONE"
                break
            try:
                json_data = json.loads(line.replace("data:", ""))
                if "choices" in json_data and len(json_data["choices"]) > 0:
                    result = ModelResponse(**json_data)
                    yield result
                    if result.choices[0].finish_reason == "stop":
                        yield "DONE"
                        break
            except json.JSONDecodeError:
                print(f"Failed to parse stream data: {line}")
                continue
                
    def create(self, parameter: BaseCompletionParameter) -> Iterator[ModelResponse]:
        """Send a completion request and handle the response.

        Args:
            parameter (BaseCompletionParameter): The completion parameters.

        Returns:
            Iterator[ModelResponse]: Stream of model responses.

        """
        count = 0
        with httpx.Client(timeout=300) as client:
            while count < self.max_retry:
                try:
                    request_json = self._prepare_request(parameter)
                    logger.info(f"LLM invoke parameters: {request_json}")
                    with client.stream(
                        "POST",
                        self.completion_url,
                        json=request_json,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                    ) as response:
                        response.raise_for_status()

                        yield from self._handle_stream_response(response)

                except Exception as e:
                    logger.error(f"Error in completions interface: {traceback.format_exc()}")
                    count += 1
                    if count >= self.max_retry:
                        raise RuntimeError(f"Max retries ({self.max_retry}) exceeded") from e


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
    def generate(self, parameter: BaseCompletionParameter) -> Iterator[ModelResponse]:
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
        # result = self.generate(parameter)
        
        token_count = 0  # 初始化 token 计数器
        for chunk in self.generate(parameter):
            if isinstance(chunk, str) and "DONE" in chunk:
                print(f"消耗token总数：{str(token_count)}")
                yield "DONE"
                break
            if chunk.choices[0].delta:
                text = chunk.choices[0].delta.content
                token_count += len(encoding.encode(text))  # 实时计算 token 数量
                yield text
                # yield f"data: {text}"  # 以 SSE（Server-Sent Events）格式返回数据
            else:
                token_count += chunk.usage.total_tokens
                print(f"返回信息：{chunk.choices[0].message.content}")
                messages = chunk.choices[0].message.content.split("\n")
                for message in messages:
                  # 将消息按行拆分，并用多个 data: 行发送
                  lines = message.split("\n\n")
                  for line in lines:
                      if not line:
                          continue
                    #   yield f"data: {line}\n\n"
                      yield line
