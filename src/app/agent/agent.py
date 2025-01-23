# agent/agent.py
from typing import List, Optional, Type, Union

import pandas as pd

from .base import BaseAgent
from .base_judge import BaseJudge
from .base_security import BaseSecurity
from src.app.components.connectors.base import BaseConnector
from src.app.components.pipelines.chat.generate_chat_pipeline import GenerateChatPipeline
from src.utils.schemas.df_config import Config
from src.app.components.vectorstores.vectorstore import VectorStore


class Agent(BaseAgent):
    def __init__(
        self,
        dfs: Union[
            pd.DataFrame, BaseConnector, List[Union[pd.DataFrame, BaseConnector]]
        ],
        config: Optional[Union[Config, dict]] = None,
        memory_size: Optional[int] = 10,
        pipeline: Optional[Type[GenerateChatPipeline]] = None,
        vectorstore: Optional[VectorStore] = None,
        description: str = None,
        judge: BaseJudge = None,
        security: BaseSecurity = None,
    ):
        super().__init__(
            dfs, config, memory_size, vectorstore, description, security=security
        )

        self.pipeline = (
            pipeline(
                self.context,
                self.logger,
                on_prompt_generation=self._callbacks.on_prompt_generation,
                on_code_generation=self._callbacks.on_code_generation,
                before_code_execution=self._callbacks.before_code_execution,
                on_result=self._callbacks.on_result,
                judge=judge,
            )
            if pipeline
            else GenerateChatPipeline(
                self.context,
                self.logger,
                on_prompt_generation=self._callbacks.on_prompt_generation,
                on_code_generation=self._callbacks.on_code_generation,
                before_code_execution=self._callbacks.before_code_execution,
                on_result=self._callbacks.on_result,
                judge=judge,
            )
        )

    @property
    def last_error(self):
        return self.pipeline.last_error

    @property
    def last_query_log_id(self):
        return self.pipeline.get_last_track_log_id()