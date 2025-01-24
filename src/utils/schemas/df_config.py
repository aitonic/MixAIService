from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator
from typing_extensions import TypedDict

from src.constants import DEFAULT_CHART_DIRECTORY
from src.utils.helpers.dataframe_serializer import DataframeSerializerType
from src.utils.llm import LLM, BambooLLM


class LogServerConfig(TypedDict):
    server_url: str
    api_key: str


class Config(BaseModel):
    save_logs: bool = True
    verbose: bool = False
    enforce_privacy: bool = False
    enable_cache: bool = True
    use_error_correction_framework: bool = True
    open_charts: bool = True
    save_charts: bool = False
    save_charts_path: str = DEFAULT_CHART_DIRECTORY
    custom_whitelisted_dependencies: list[str] = Field(default_factory=list)
    max_retries: int = 3
    lazy_load_connector: bool = True
    response_parser: Any = None
    llm: LLM = None
    data_viz_library: str | None = ""
    log_server: LogServerConfig = None
    direct_sql: bool = False
    dataframe_serializer: DataframeSerializerType = DataframeSerializerType.CSV
    security: Literal["standard", "none", "advanced"] = "standard"

    class Config:
        arbitrary_types_allowed = True

    @field_validator("llm")
    def validate_llm(cls, llm) -> LLM:
        if not isinstance(llm, (LLM)):  # also covers llm is None
            return BambooLLM()
        return llm
