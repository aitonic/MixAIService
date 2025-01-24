import os
import re
from abc import ABC
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ..base_component import BaseComponent


class BasePrompt(ABC, BaseComponent):
    """Abstract class for generating system and user messages."""

    template: str | None = None
    template_path: str | None = None

    def __init__(self, **kwargs) -> None:
        self.props = kwargs

        if self.template:
            env = Environment()
            self.prompt = env.from_string(self.template)
        elif self.template_path:
            # Find path to template file
            current_dir_path = Path(__file__).parent
            path_to_template = os.path.join(current_dir_path, "templates")
            env = Environment(loader=FileSystemLoader(path_to_template))
            self.prompt = env.get_template(self.template_path)

        self._resolved_prompt = None


    def render(self) -> str:
        """Render the prompt using provided properties."""
        render = self.prompt.render(**self.props)

        # Remove additional newlines in render
        render = re.sub(r"\n{3,}", "\n\n", render)

        return render

    def to_string(self) -> str:
        """Render the prompt and cache the result."""
        if self._resolved_prompt is None:
            self._resolved_prompt = self.render()

        return self._resolved_prompt

    def __str__(self) -> str:
        return self.to_string()

    def validate(self, output: str) -> bool:
        """Validate the output of the prompt."""
        return isinstance(output, str)

    def to_json(self) -> dict:
        """Return the prompt in JSON format."""
        if "context" not in self.props:
            return {"prompt": self.to_string()}

        context = self.props["context"]
        memory = context.memory
        conversations = memory.to_json()
        system_prompt = memory.get_system_prompt()
        return {
            "conversation": conversations,
            "system_prompt": system_prompt,
            "prompt": self.to_string(),
        }
