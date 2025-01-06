from pydantic import BaseModel, Field


class MessageInfo(BaseModel):
    """保存的消息"""

    # 消息id
    id: str | None = Field(None)
    # 用户身份识别,比如api_key
    user_id: str
    system_message: str | None = Field(None)
    user_message: str | None = Field(None)
    assistant_message: str | None = Field(None)
    # 创建时间
    created: float | None = Field(0)


class MessageListParameter(BaseModel):
    """查询消息列表的参数"""

    # 用户身份识别
    api_key: str
    # 取出的条数
    limit: int = 3
    # 倒序，取最近的数据
    desc: bool = True
    # 开始时间
    created: float = 0
