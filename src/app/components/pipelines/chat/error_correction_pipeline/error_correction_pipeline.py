# app/model_components/pipelines/chat/error_correction_pipeline/error_correction_pipeline.py
from typing import Optional

from src.utils.logger import Logger
from src.utils.helpers.query_exec_tracker import QueryExecTracker
from src.app.components.pipelines.chat.code_cleaning import CodeCleaning
from src.app.components.pipelines.chat.code_generator import CodeGenerator
from src.app.components.pipelines.chat.error_correction_pipeline.error_correction_pipeline_input import (
    ErrorCorrectionPipelineInput,
)
from src.app.components.pipelines.chat.error_correction_pipeline.error_prompt_generation import (
    ErrorPromptGeneration,
)
from src.app.components.pipelines.core.pipeline import Pipeline
from src.app.components.pipelines.core.pipeline_context import PipelineContext


class ErrorCorrectionPipeline:
    """
    Error Correction Pipeline to regenerate prompt and code
    """

    _context: PipelineContext
    _logger: Logger

    def __init__(
        self,
        context: Optional[PipelineContext] = None,
        logger: Optional[Logger] = None,
        query_exec_tracker: QueryExecTracker = None,
        on_prompt_generation=None,
        on_code_generation=None,
    ):
        self.pipeline = Pipeline(
            context=context,
            logger=logger,
            query_exec_tracker=query_exec_tracker,
            steps=[
                ErrorPromptGeneration(on_prompt_generation=on_prompt_generation),
                CodeGenerator(on_execution=on_code_generation),
                CodeCleaning(),
            ],
        )
        self._context = context
        self._logger = logger

    def run(self, input: ErrorCorrectionPipelineInput):
        self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")
        return self.pipeline.run(input)
