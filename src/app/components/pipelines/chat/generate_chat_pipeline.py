# app/model_components/pipelines/chat/generate_chat_pipeline.py
from typing import TYPE_CHECKING

from src.app.agent.base_judge import BaseJudge

if TYPE_CHECKING:
    from src.utils.helpers.query_exec_tracker import QueryExecTracker

from src.app.components.pipelines.chat.cache_lookup import CacheLookup
from src.app.components.pipelines.chat.cache_population import CachePopulation
from src.app.components.pipelines.chat.chat_pipeline_input import (
    ChatPipelineInput,
)
from src.app.components.pipelines.chat.code_cleaning import CodeCleaning
from src.app.components.pipelines.chat.code_execution import CodeExecution
from src.app.components.pipelines.chat.code_execution_pipeline_input import (
    CodeExecutionPipelineInput,
)
from src.app.components.pipelines.chat.code_generator import CodeGenerator
from src.app.components.pipelines.chat.error_correction_pipeline.error_correction_pipeline import (
    ErrorCorrectionPipeline,
)
from src.app.components.pipelines.chat.error_correction_pipeline.error_correction_pipeline_input import (
    ErrorCorrectionPipelineInput,
)
from src.app.components.pipelines.chat.prompt_generation import PromptGeneration
from src.app.components.pipelines.chat.result_parsing import ResultParsing
from src.app.components.pipelines.chat.result_validation import ResultValidation
from src.app.components.pipelines.chat.validate_pipeline_input import (
    ValidatePipelineInput,
)
from src.app.components.pipelines.core.pipeline import Pipeline
from src.app.components.pipelines.core.pipeline_context import PipelineContext
from src.utils.logger import Logger


class GenerateChatPipeline(Pipeline): # 继承 Pipeline
    code_generation_pipeline = Pipeline
    code_execution_pipeline = Pipeline
    context: PipelineContext
    _logger: Logger
    last_error: str
    tracker: 'QueryExecTracker'

    def __init__(
        self,
        context: PipelineContext | None = None,
        logger: Logger | None = None,
        judge: BaseJudge = None,
        on_prompt_generation=None,
        on_code_generation=None,
        before_code_execution=None,
        on_result=None,
        tracker: 'QueryExecTracker' = None,
    ):
        self.tracker = tracker  # 先设置 tracker
        super().__init__( # 调用父类 Pipeline 的 __init__ 方法
            context=context, # 传递 context 参数
            logger=logger, # 传递 logger 参数
            query_exec_tracker=tracker,
            steps=[ # 定义 steps
                ValidatePipelineInput(),
                CacheLookup(),
                PromptGeneration(
                    skip_if=self.is_cached,
                    on_execution=on_prompt_generation,
                ),
                CodeGenerator(
                    skip_if=self.is_cached,
                    on_execution=on_code_generation,
                ),
                CachePopulation(skip_if=self.is_cached),
                CodeCleaning(
                    skip_if=self.no_code,
                    on_failure=self.on_code_cleaning_failure,
                    on_retry=self.on_code_retry,
                ),
            ],
        )

        self.code_execution_pipeline = Pipeline( # 创建 code_execution_pipeline
            context=context,
            logger=logger,
            query_exec_tracker=self.tracker,
            steps=[
                CodeExecution(
                    before_execution=before_code_execution,
                    on_failure=self.on_code_execution_failure,
                    on_retry=self.on_code_retry,
                ),
                ResultValidation(),
                ResultParsing(
                    before_execution=on_result,
                ),
            ],
        )

        self.code_exec_error_pipeline = ErrorCorrectionPipeline( # 创建 code_exec_error_pipeline
            context=context,
            logger=logger,
            query_exec_tracker=self.tracker,
            on_code_generation=on_code_generation,
            on_prompt_generation=on_prompt_generation,
        )

        self.judge = judge

        if self.judge:
            if self.judge.pipeline.pipeline.context:
                self.judge.pipeline.pipeline.context.memory = context.memory
            else:
                self.judge.pipeline.pipeline.context = context

            self.judge.pipeline.pipeline.logger = logger
            self.judge.pipeline.pipeline.query_exec_tracker = self.tracker

        self.context = context
        self._logger = logger
        self.last_error = None
        self.tracker = tracker

    def on_code_execution_failure(self, code: str, errors: Exception) -> str:
        """Executes on code execution failure
        Args:
            code (str): code that is ran
            exception (Exception): exception that is raised during code execution

        Returns:
            str: returns the updated code with the fixes

        """
        # Add information about the code failure in the query tracker for debug
        self.tracker.add_step(
            {
                "type": "CodeExecution",
                "success": False,
                "message": "Failed to execute code",
                "execution_time": None,
                "data": {
                    "content_type": "code",
                    "value": code,
                    "exception": errors,
                },
            }
        )

    def on_code_cleaning_failure(self, code, errors):
        # Add information about the code failure in the query tracker for debug
        self.tracker.add_step(
            {
                "type": "CodeCleaning",
                "success": False,
                "message": "Failed to clean code",
                "execution_time": None,
                "data": {
                    "content_type": "code",
                    "value": code,
                    "exception": errors,
                },
            }
        )

    def on_code_retry(self, code: str, exception: Exception):
        correction_input = ErrorCorrectionPipelineInput(code, exception)
        return self.code_exec_error_pipeline.run(correction_input)

    def no_code(self, context: PipelineContext):
        return context.get("last_code_generated") is None

    def is_cached(self, context: PipelineContext):
        return context.get("found_in_cache")

    def get_last_track_log_id(self):
        return self.tracker.last_log_id

    def run_generate_code(self, input: ChatPipelineInput) -> dict:
        """Executes the code generation pipeline with user input and return the result
        Args:
            input (ChatPipelineInput): _description_

        Returns:
            The `output` dictionary is expected to have the following keys:
            - 'type': The type of the output.
            - 'value': The value of the output.

        """
        self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")

        # Reset intermediate values
        self.context.reset_intermediate_values()

        # Start New Tracking for Query
        self.tracker.start_new_track(input)

        self.tracker.add_skills(self.context)

        self.tracker.add_dataframes(self.context.dfs)

        # Add Query to memory
        self.context.memory.add(input.query, True)

        self.context.add_many(
            {
                "output_type": input.output_type,
                "last_prompt_id": input.prompt_id,
            }
        )
        try:
            output = self.code_generation_pipeline.run(input)

            self.tracker.success = True

            self.tracker.publish()

            return output

        except Exception as e:
            # Show the full traceback
            import traceback

            traceback.print_exc()

            self.last_error = str(e)
            self.tracker.success = False
            self.tracker.publish()

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{e}\n"
            )

    def run_execute_code(self, input: CodeExecutionPipelineInput) -> dict:
        """Executes the chat pipeline with user input and return the result
        Args:
            input (CodeExecutionPipelineInput): _description_

        Returns:
            The `output` dictionary is expected to have the following keys:
            - 'type': The type of the output.
            - 'value': The value of the output.

        """
        self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")

        # Reset intermediate values
        self.context.reset_intermediate_values()

        # Start New Tracking for Query
        self.tracker.start_new_track(input)

        self.tracker.add_skills(self.context)

        self.tracker.add_dataframes(self.context.dfs)

        # Add Query to memory
        self.context.memory.add(input.code, True)

        self.context.add_many(
            {
                "output_type": input.output_type,
                "last_prompt_id": input.prompt_id,
            }
        )
        try:
            output = self.code_execution_pipeline.run(input.code)

            self.tracker.success = True

            self.tracker.publish()

            return output

        except Exception as e:
            # Show the full traceback
            import traceback

            traceback.print_exc()

            self.last_error = str(e)
            self.tracker.success = False
            self.tracker.publish()

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{e}\n"
            )

    def run(self, input: ChatPipelineInput) -> dict:
        """Executes the chat pipeline with user input and return the result
        Args:
            input (ChatPipelineInput): _description_

        Returns:
            The `output` dictionary is expected to have the following keys:
            - 'type': The type of the output.
            - 'value': The value of the output.

        """
        self._logger.log(f"Executing Pipeline: {self.__class__.__name__}")

        # Reset intermediate values
        self.context.reset_intermediate_values()

        # Start New Tracking for Query
        self.tracker.start_new_track(input)

        self.tracker.add_skills(self.context)

        self.tracker.add_dataframes(self.context.dfs)

        # Add Query to memory
        self.context.memory.add(input.query, True)

        self.context.add_many(
            {
                "output_type": input.output_type,
                "last_prompt_id": input.prompt_id,
            }
        )
        try:
            if self.judge:
                code = self.code_generation_pipeline.run(input)

                retry_count = 0
                while retry_count < self.context.config.max_retries:
                    if self.judge.evaluate(query=input.query, code=code):
                        break
                    code = self.code_generation_pipeline.run(input)
                    retry_count += 1

                output = self.code_execution_pipeline.run(code)

            elif self.code_execution_pipeline:
                output = (
                    self.code_generation_pipeline | self.code_execution_pipeline
                ).run(input)
            else:
                output = self.code_generation_pipeline.run(input)

            self.tracker.success = True

            self.tracker.publish()

            return output

        except Exception as e:
            # Show the full traceback
            import traceback

            traceback.print_exc()

            self.last_error = str(e)
            self.tracker.success = False
            self.tracker.publish()

            return (
                "Unfortunately, I was not able to answer your question, "
                "because of the following error:\n"
                f"\n{e}\n"
            )
