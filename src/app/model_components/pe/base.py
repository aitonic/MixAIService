from abc import ABC, abstractmethod
from ..base_component import BaseComponent
from pydantic import Field


class AbsPrompt(ABC, BaseComponent):
    """抽象类，用于生成系统和用户消息。"""

    # system和user两种
    role: str = Field(description="角色")
    content: str = Field(description="内容")

    def __init__(self, role: str, prompt_str: str) -> None:
        self.content = prompt_str
        self.role = role

    @abstractmethod
    def generate_prompt(self, params: dict) -> str:
        """根据参数处理prompt。"""
        pass
