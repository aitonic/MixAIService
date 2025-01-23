from pydantic import BaseModel, Field


class MessageInfo(BaseModel):
    """保存的消息"""

    # Message ID
    id: str | None = Field(None)
    # User identification, e.g. api_key
    user_id: str
    system_message: str | None = Field(None)
    user_message: str | None = Field(None)
    assistant_message: str | None = Field(None)
    # start timestamp
    created: float | None = Field(0)


class MessageListParameter(BaseModel):
    """查询消息列表的参数"""

    # User identification
    api_key: str
    # Number of records to fetch
    limit: int = 3
    # Descending order, get latest data
    desc: bool = True
    # Start timestamp
    created: float = 0
