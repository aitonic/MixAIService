from collections.abc import Mapping
from typing import Any

from jinja2 import Environment, Template, meta

from .base import BasePrompt


class BasePrompt(BasePrompt):
    """Base prompt class.
    
    Uses Jinja2 as template processor.
    """

    def __init__(self, role: str, prompt_str: str) -> None:
        """Initialize the prompt.

        Args:
            role (str): Role of the prompt (system/user).
            prompt_str (str): Prompt template string.

        """
        # super().__init__(role, prompt_str)
        self.role = role
        self.content = prompt_str

    def generate_prompt(self, params: dict) -> str:
        """Generate prompt by processing template with given parameters.

        Args:
            params (dict): Parameters to replace in the template.

        Returns:
            str: The processed prompt string.

        Raises:
            ValueError: If any required parameter is missing.

        """
        # Create Jinja2 environment
        env = Environment(autoescape=True)

        # Parse template source code to generate AST
        parsed_content = env.parse(self.content)

        # Extract undeclared variables
        undeclared_variables = meta.find_undeclared_variables(parsed_content)

        if not undeclared_variables:
            # No variables to replace, return as is
            return self

        # Validate all required parameters are provided
        for var in undeclared_variables:
            if var not in params:
                raise ValueError(f"Missing parameter: {var}")
                
        self.content = Template(self.content).render(params)
        return self

    def __call__(self, *args: tuple[object, ...], **kwds: Mapping[str, Any]) -> str: # noqa: N807
        """Call the object to generate prompt.

        Args:
            *args: Tuple of arguments of any type.
            **kwds: Mapping of parameters with string keys.

        Returns:
            str: The generated prompt.

        """
        return self.generate_prompt(args[0])

    def as_parameter(self) -> dict:
        """Return the attribute dictionary of the object.

        Returns:
            dict: The attribute dictionary of the current object.

        """
        return self.__dict__


class SystemPrompt(BasePrompt):
    def __init__(self, system_prompt: str) -> None:
        super().__init__("system", system_prompt)

    def generate_prompt(self, params: dict) -> BasePrompt:
        return super().generate_prompt(params)


class HumanPrompt(BasePrompt):
    def __init__(self, human_message: str) -> None:
        super().__init__("user", human_message)

    def generate_prompt(self, params: dict) -> BasePrompt:
        return super().generate_prompt(params)
