"""
Pipeline Factory Module

This module provides a factory class for creating and configuring various pipeline instances. 
It supports different types of pipelines such as chat, error correction, semantic chat, and agent-based pipelines.

Classes:
    PipelineFactory: A factory for creating specific types of pipelines based on input parameters.

Author: ai
Created: 2025-01-19
"""

from src.app.components.pipelines.core.pipeline import Pipeline
from src.app.components.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline
from src.app.components.pipelines.chat.error_correction_pipeline.error_correction_pipeline import ErrorCorrectionPipeline
# from app.model_components.pipelines.ee.semantic_agent.pipeline.semantic_chat_pipeline import SemanticChatPipeline
# from app.model_components.pipelines.ee.agents.judge_agent.pipeline.judge_pipeline import JudgePipeline
# from app.model_components.pipelines.ee.agents.advanced_security_agent.pipeline.advanced_security_pipeline import AdvancedSecurityPipeline


class PipelineFactory:
    """
    Factory class for creating and configuring various Pipeline instances.
    """
    
    def create_pipeline(
        self,
        pipeline_type: str,
        context,
        logger,
        query_exec_tracker=None,
        judge=None,
        on_prompt_generation=None,
        on_code_generation=None,
        before_code_execution=None,
        on_result=None,
    ) -> Pipeline:
        """
        Create and return a pipeline instance based on the given pipeline type.

        Args:
            pipeline_type (str): Type of the pipeline (e.g., "chat", "error_correction", "semantic_chat").
            context: Pipeline context required for execution.
            logger: Logger instance for logging pipeline activities.
            query_exec_tracker: Query execution tracker (optional).
            judge: Judge Agent for decision-making (optional).
            on_prompt_generation (Callable): Callback for prompt generation (optional).
            on_code_generation (Callable): Callback for code generation (optional).
            before_code_execution (Callable): Callback before code execution (optional).
            on_result (Callable): Callback for handling the result (optional).

        Returns:
            Pipeline: An instance of the specified pipeline.

        Raises:
            ValueError: If the specified `pipeline_type` is unknown.
        """
        if pipeline_type == "chat":
            return GenerateChatPipeline(
                context=context,
                logger=logger,
                query_exec_tracker=query_exec_tracker,
                judge=judge,
                on_prompt_generation=on_prompt_generation,
                on_code_generation=on_code_generation,
                before_code_execution=before_code_execution,
                on_result=on_result,
            )
        elif pipeline_type == "error_correction":
            return ErrorCorrectionPipeline(
                context=context,
                logger=logger,
                query_exec_tracker=query_exec_tracker,
                on_prompt_generation=on_prompt_generation,
                on_code_generation=on_code_generation,
            )
        # elif pipeline_type == "semantic_chat":
        #     return SemanticChatPipeline(
        #         context=context,
        #         logger=logger,
        #         query_exec_tracker=query_exec_tracker,
        #         judge=judge,
        #         on_prompt_generation=on_prompt_generation,
        #         on_code_generation=on_code_generation,
        #         before_code_execution=before_code_execution,
        #         on_result=on_result,
        #     )
        # elif pipeline_type == "judge_agent":
        #     return JudgePipeline(
        #         context=context,
        #         logger=logger,
        #         query_exec_tracker=query_exec_tracker,
        #     )
        # elif pipeline_type == "advanced_security_agent":
        #     return AdvancedSecurityPipeline(
        #         context=context,
        #         logger=logger,
        #         query_exec_tracker=query_exec_tracker,
            # )
        else:
            raise ValueError(f"Unknown pipeline type: {pipeline_type}")