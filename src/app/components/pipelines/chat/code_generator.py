# app/model_components/pipelines/chat/code_generator.py
from typing import Any

from src.app.components.pipelines.logic_unit_output import LogicUnitOutput

from src.utils.logger import Logger
from src.app.components.pipelines.core.base_logic_unit import BaseLogicUnit
from src.app.components.pipelines.core.pipeline_context import PipelineContext


class CodeGenerator(BaseLogicUnit):
    """
    LLM Code Generation Stage
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
        """
        This method will return output according to
        Implementation.

        :param input: Your input data.
        :param kwargs: A dictionary of keyword arguments.
            - 'logger' (any): The logger for logging.
            - 'config' (Config): Global configurations for the test
            - 'context' (any): The execution context.

        :return: The result of the execution.
        """
        pipeline_context: PipelineContext = kwargs.get("context")
        logger: Logger = kwargs.get("logger")

        code = pipeline_context.config.llm.generate_code(input, pipeline_context)

        pipeline_context.add("last_code_generated", code)
        logger.log(
            f"""Prompt used:
            {pipeline_context.config.llm.last_prompt}
            """
        )
        logger.log(
            f"""Code generated:
            ```
            {code}
            ```
            """
        )

        return LogicUnitOutput(
            code,
            True,
            "Code Generated Successfully",
            {"content_type": "code", "value": code},
        )
