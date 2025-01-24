"""Fake LLM"""


from src.app.components.pipelines.core.pipeline_context import PipelineContext
from src.app.components.prompts.base import BasePrompt

from .base import LLM


class FakeLLM(LLM):
    """Fake LLM"""

    _output: str = """result = { 'type': 'string', 'value': "Hello World" }"""

    def __init__(self, output: str | None = None):
        if output is not None:
            self._output = output

    def call(self, instruction: BasePrompt, context: PipelineContext = None) -> str:
        self.last_prompt = instruction.to_string()
        return self._output

    @property
    def type(self) -> str:
        return "fake"
