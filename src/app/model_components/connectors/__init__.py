# app/model_components/connectors/__init__.py
from typing import Union

from app.model_components.connectors.base import BaseConnector
from app.model_components.connectors.pandas import PandasConnector, PandasConnectorConfig
from app.model_components.connectors.sql import SQLConnector, SQLConnectorConfig, SqliteConnector, SqliteConnectorConfig, MySQLConnector, MySQLConnectorConfig, PostgreSQLConnector, PostgreSQLConnectorConfig, OracleConnector, OracleConnectorConfig
from app.model_components.connectors.airtable import AirtableConnector, AirtableConnectorConfig
from app.model_components.connectors.yahoo_finance import YahooFinanceConnector, YahooFinanceConnectorConfig

class ConnectorFactory:
    """
    Connector 工厂类，用于创建和配置各种 Connector 实例
    """

    def create_connector(self, connector_type: str, config: Union[dict, PandasConnectorConfig, SQLConnectorConfig, SqliteConnectorConfig, MySQLConnectorConfig, PostgreSQLConnectorConfig, OracleConnectorConfig, AirtableConnectorConfig, YahooFinanceConnectorConfig], **kwargs) -> BaseConnector:
        """
        根据 connector_type 和 config 创建不同类型的 Connector 实例

        Args:
            connector_type (str): Connector 类型 (例如 "pandas", "sql", "sqlite", "airtable" 等)
            config (Union[dict, ConnectorConfig]): Connector 配置信息

        Returns:
            BaseConnector: Connector 实例
        """
        if connector_type == "pandas":
            return PandasConnector(config=config, **kwargs)
        elif connector_type == "sql":
            return SQLConnector(config=config, **kwargs)
        elif connector_type == "sqlite":
            return SqliteConnector(config=config, **kwargs)
        elif connector_type == "mysql":
            return MySQLConnector(config=config, **kwargs)
        elif connector_type == "postgresql":
            return PostgreSQLConnector(config=config, **kwargs)
        elif connector_type == "oracle":
            return OracleConnector(config=config, **kwargs)
        elif connector_type == "airtable":
            return AirtableConnector(config=config, **kwargs)
        elif connector_type == "yahoo_finance":
            return YahooFinanceConnector(config=config, **kwargs)
        else:
            raise ValueError(f"Unknown connector type: {connector_type}")


__all__ = [
    "BaseConnector",
    "PandasConnector",
    "PandasConnectorConfig",
    "SQLConnector",
    "SQLConnectorConfig",
    "SqliteConnector",
    "SqliteConnectorConfig",
    "MySQLConnector",
    "MySQLConnectorConfig",
    "PostgreSQLConnector",
    "PostgreSQLConnectorConfig",
    "OracleConnector",
    "OracleConnectorConfig",
    "AirtableConnector",
    "AirtableConnectorConfig",
    "YahooFinanceConnector",
    "YahooFinanceConnectorConfig",
    "ConnectorFactory", # 将 ConnectorFactory 加入 __all__
]