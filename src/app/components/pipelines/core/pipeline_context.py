# app/model_components/pipelines/core/pipeline_context.py
from typing import Any

from src.app.components.connectors import BaseConnector
from src.app.components.vectorstores import VectorStore
from src.utils.helpers.cache import Cache
from src.utils.helpers.memory import Memory
from src.utils.helpers.skills_manager import SkillsManager
from src.utils.schemas.df_config import Config


class PipelineContext:
    """Pass Context to the pipeline which is accessible to each step via kwargs
    """

    def __init__(
        self,
        dfs: list[BaseConnector],
        config: Config | dict | None = None,
        memory: Memory | None = None,
        skills_manager: SkillsManager | None = None,
        cache: Cache | None = None,
        vectorstore: VectorStore = None,
        initial_values: dict = None,
    ) -> None:
        if isinstance(config, dict):
            config = Config(**config)

        self.dfs = dfs
        self.memory = memory or Memory()
        self.skills_manager = skills_manager or SkillsManager()

        if config.enable_cache:
            self.cache = cache if cache is not None else Cache()
        else:
            self.cache = None

        self.config = config

        self.intermediate_values = initial_values or {}

        self.vectorstore = vectorstore

        self._initial_values = initial_values

    def reset_intermediate_values(self):
        self.intermediate_values = self._initial_values or {}

    def add(self, key: str, value: Any):
        self.intermediate_values[key] = value

    def add_many(self, values: dict):
        self.intermediate_values.update(values)

    def get(self, key: str, default: Any = ""):
        return self.intermediate_values.get(key, default)
