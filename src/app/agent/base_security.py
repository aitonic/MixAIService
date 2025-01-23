# agent/base_security.py
from src.utils.logger import Logger
from src.app.components.pipelines.core.pipeline import Pipeline
from src.app.components.pipelines.core.pipeline_context import PipelineContext


class BaseSecurity:
    context: PipelineContext
    pipeline: Pipeline
    logger: Logger

    def __init__(
        self,
        pipeline: Pipeline,
    ) -> None:
        self.pipeline = pipeline

    def evaluate(self, query: str) -> bool:
        raise NotImplementedError