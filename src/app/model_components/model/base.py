import os
from abc import ABC, abstractmethod

from .constants import DEFAULT_COMPLETION_PATH
from .dto import BaseLLMParameter, ModelResponse


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

    @abstractmethod
    def completion(self, **args):
        raise Exception("Not implemented completion method")

    def after_response(self, response: ModelResponse):
        # 保存日志
        pass
