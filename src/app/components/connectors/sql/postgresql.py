# app/model_components/connectors/sql/postgresql.py
"""PostgreSQL connectors are used to connect to PostgreSQL databases.
"""

from functools import cache

import sqlglot

# from src.app.components.connectors.base import BaseConnectorConfig # 修改 import 路径
from src.app.components.connectors.sql.sql import SQLConnector  # 修改 import 路径
from src.app.components.connectors.sql.sql_connector_config import (
    SQLConnectorConfig,  # 修改 import 路径
)
from src.utils.pandas import pd


class PostgreSQLConnector(SQLConnector):
    """PostgreSQL connectors are used to connect to PostgreSQL databases.
    """

    def __init__(
        self,
        config: SQLConnectorConfig | dict,
        **kwargs,
    ):
        """Initialize the PostgreSQL connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the PostgreSQL connector.

        """
        if "dialect" not in config:
            config["dialect"] = "postgresql"

        config["driver"] = "psycopg2"

        if isinstance(config, dict):
            postgresql_env_vars = {
                "host": "POSTGRESQL_HOST",
                "port": "POSTGRESQL_PORT",
                "database": "POSTGRESQL_DATABASE",
                "username": "POSTGRESQL_USERNAME",
                "password": "POSTGRESQL_PASSWORD",
            }
            config = self._populate_config_from_env(config, postgresql_env_vars)

        super().__init__(config, **kwargs)

    @cache
    def head(self, n: int = 5) -> pd.DataFrame:
        """Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the data source.

        Returns:
            DataFrame: The head of the data source.

        """
        if self.logger:
            self.logger.log(
                f"Getting head of {self.config.table} "
                f"using dialect {self.config.dialect}"
            )

        # Run a SQL query to get all the columns names and 5 random rows
        query = self._build_query(limit=n, order="RANDOM()")

        # Return the head of the data source
        return pd.read_sql(query, self._connection)

    @property
    def cs_table_name(self):
        return f'"{self.config.table}"'

    def execute_direct_sql_query(self, sql_query):
        sql_query = sqlglot.transpile(sql_query, read="mysql", write="postgres")[0]
        return super().execute_direct_sql_query(sql_query)
