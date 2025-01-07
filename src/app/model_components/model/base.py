import os
from abc import ABC, abstractmethod
import httpx
import traceback
from src.utils.logger import logger
from .constants import (
    DEFAULT_COMPLETION_PATH,
    DEFAULT_EMBEDDING_PATH
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
    
    def create(self, parameter: BaseCompletionParameter) -> dict:
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
                    return response
                except Exception as e:
                    logger.error(f"completions接口出错：{traceback.format_exc()}")
                    count = count+1
            # 如果不使用流式返回
            
            # result = MixResponse(**data)  # 将响应数据映射到模型
            # yield result.choices[0].message.content

class Embeddings:
    suffix = DEFAULT_EMBEDDING_PATH

    def __init__(self) -> None:
        pass

    def create(self):
        pass


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
    def completion_url(self):
        if self.full_url:
            return self.full_url
        return self.base_url + DEFAULT_COMPLETION_PATH
    
    @property
    def embed_url(self):
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
    def embeddings(self) -> "AbsLLMModel":
        return self

    @abstractmethod
    def generate(self, parameter: BaseCompletionParameter):
        raise Exception("Not implemented completion method")

    def after_response(self, response: ModelResponse):
        # 保存日志
        pass
