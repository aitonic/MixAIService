from abc import ABC, abstractmethod

from pydantic import Field

from ..base_component import BaseComponent


class AbsPrompt(ABC, BaseComponent):
    """Abstract class for generating system and user messages."""

    # system和user两种
    role: str = Field(description="content role")
    content: str = Field(description="content")

    def __init__(self, role: str, prompt_str: str) -> None:
        self.content = prompt_str
        self.role = role

    @abstractmethod
    def generate_prompt(self, params: dict) -> str:
        """Generate prompt based on parameters.

        Args:
            params (dict): Parameters used to generate the prompt.

        Returns:
            str: The generated prompt string.
        """
        pass
