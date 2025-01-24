##agent/base_judge.py
from typing import TYPE_CHECKING

from src.app.components.pipelines.core.pipeline_context import PipelineContext
from src.utils.logger import Logger

if TYPE_CHECKING:
    from src.app.components.pipelines.core.pipeline import Pipeline


class BaseJudge:
    context: PipelineContext
    pipeline: 'Pipeline'
    logger: Logger

    def __init__(
        self,
        pipeline: 'Pipeline',
    ) -> None:
        self.pipeline = pipeline

    def evaluate(self, query: str, code: str) -> bool:
        raise NotImplementedError
