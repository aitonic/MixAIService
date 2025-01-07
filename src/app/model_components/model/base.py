import os
from abc import ABC, abstractmethod
from typing import Any, Never

from src.utils.logger import logger

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
    def completion_url(self) -> str:
        if self.full_url:
            return self.full_url
        return self.base_url + DEFAULT_COMPLETION_PATH

    @abstractmethod
    def completion(self, **args: dict[str, Any]) -> Never:
        """抽象方法，负责实现具体的完成逻辑。

        Args:
            **args (dict[str, Any]): 参数字典，键为字符串，值为任意类型。

        Raises:
            Exception: 如果子类未实现该方法。

        """
        raise Exception("Not implemented completion method")

    # @abstractmethod
    def after_response(self, response: ModelResponse) -> None:
        """在模型响应后执行的操作。

        Args:
            response (ModelResponse): 模型的响应对象。

        """
        logger.info(f"Processing response: {response}")
        
