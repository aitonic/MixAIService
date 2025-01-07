import os
from abc import ABC, abstractmethod
import httpx
import traceback
import json
from typing import Iterator
from src.utils.logger import logger
from .constants import (
    DEFAULT_COMPLETION_PATH,
    DEFAULT_EMBEDDING_PATH,
    DEFAULT_EMBED_MODEL
)
from .dto import (
    BaseLLMParameter, 
    ModelResponse, 
    BaseCompletionParameter,
    BaseMessage
)

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
    def completion_url(self):
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

                        yield result.choices[0].message.content
                    # 使用流式返回
                    for line in response.iter_lines():
                        if line:
                            if "DONE" in line.decode("utf-8"):
                                return
                            # 去掉 'data:' 前缀并解析 JSON 数据
                            data = json.loads(line.decode("utf-8").replace("data:", ""))
                            result = ModelResponse(**data)
                            yield result.choices[0].delta.content
                except Exception as e:
                    logger.error(f"completions接口出错：{traceback.format_exc()}")
                    count = count+1
            # 如果不使用流式返回
            
            # result = MixResponse(**data)  # 将响应数据映射到模型
            # yield result.choices[0].message.content

class Embeddings:
    suffix = DEFAULT_EMBEDDING_PATH

    def __init__(self, api_key: str = None,
                        base_url: str = None,
                        full_url: str = None,
                        max_retry: int = 3) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.full_url = full_url
        self.max_retry = max_retry

    @property
    def embed_url(self) -> str:
        if self.full_url:
            return self.full_url
        return self.base_url + DEFAULT_EMBEDDING_PATH
    
    def create(self, text: str, model: str = DEFAULT_EMBED_MODEL, encoding_format:str = "float"):
        """调用embedding接口的方法，出入参和openai一致。

        参数:
            input_data (str): 输入数据，待嵌入的文本。
            model (str): 使用的模型名称，默认为"text-embedding-ada-002"。
            user (str): 用户标识，可选参数。

        返回:
            dict: 包含嵌入结果的字典。
        """
        url = self.embed_url
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "input": text,
            "model": model,
            "encoding_format": encoding_format
        }
        
        import httpx

        with httpx.Client(timeout=30) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()


class AbsLLMModel(ABC):
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
    def embeddings(self) -> Embeddings:
        return Embeddings(api_key=self.api_key, base_url=self.base_url, full_url=self.full_url, max_retry=self.max_retry)

    @abstractmethod
    def generate(self, parameter: BaseCompletionParameter):
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
        
