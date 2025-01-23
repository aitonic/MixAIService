# app/model_components/pipelines/chat/validate_pipeline_input.py
from typing import Any, List

from app.model_components.connectors.pandas import PandasConnector
from app.model_components.connectors.sql import SQLConnector
from src.utils.exceptions import InvalidConfigError
from app.model_components.pipelines.logic_unit_output import LogicUnitOutput

from app.model_components.connectors import BaseConnector
from app.model_components.pipelines.core.base_logic_unit import BaseLogicUnit
from app.model_components.pipelines.core.pipeline_context import PipelineContext


class ValidatePipelineInput(BaseLogicUnit):
    """
    Validates pipeline input
    """

    pass

    def _validate_direct_sql(self, dfs: List[BaseConnector]) -> bool:
        """
        Raises error if they don't belong sqlconnector or have different credentials
        Args:
            dfs (List[BaseConnector]): list of BaseConnectors

        Raises:
            InvalidConfigError: Raise Error in case of config is set but criteria is not met
        """

        if self.context.config.direct_sql:
            if all(
                (isinstance(df, SQLConnector) and df.equals(dfs[0])) for df in dfs
            ) or all(
                (isinstance(df, PandasConnector) and df.sql_enabled) for df in dfs
            ):
                return True
            else:
                raise InvalidConfigError(
                    "Direct requires all Connector and they belong to same datasource "
                    "and have same credentials"
                )
        return False

    def execute(self, input: Any, **kwargs) -> Any:
        """
        This method validates pipeline context and configs

        :param input: Your input data.
        :param kwargs: A dictionary of keyword arguments.
            - 'logger' (any): The logger for logging.
            - 'config' (Config): Global configurations for the test
            - 'context' (any): The execution context.

        :return: The result of the execution.
        """
        self.context: PipelineContext = kwargs.get("context")
        self._validate_direct_sql(self.context.dfs)
        return LogicUnitOutput(input, True, "Input Validation Successful")
