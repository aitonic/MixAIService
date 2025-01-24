# app/model_components/connectors/sql/sql_connector_config.py

from src.app.components.connectors.base import BaseConnectorConfig  # 修改 import 路径


class SQLBaseConnectorConfig(BaseConnectorConfig):
    """Base Connector configuration.
    """

    driver: str | None = None
    dialect: str | None = None


class SqliteConnectorConfig(SQLBaseConnectorConfig):
    """Connector configurations for sqlite db.
    """

    table: str
    database: str


class SQLConnectorConfig(SQLBaseConnectorConfig):
    """Connector configuration.
    """

    host: str
    port: int
    username: str
    password: str
