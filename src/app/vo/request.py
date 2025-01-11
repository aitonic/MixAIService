
from pydantic import BaseModel, Field


class RunData(BaseModel):
    query:str = Field(description="调用的数据")
    base_url:str | None = Field(default = None, description="模型（completions/embeddings）的基础url，例如:http://127.0.0.1:1234")
    full_url:str | None = Field(default = None, description="模型（completions/embeddings）的全路径url，当不是openai格式的地址的时候，需要指定")
    system_prompt:str | None = Field(default = None, description="system message")
    search_collections:list[str] | None = Field(default = None, description="vector检索的时候，可以指定检索的collection")
    collection_name:str | None = Field(default = None, description="vector添加文本的时候，可以指定检索的collection")


    class Config:
        """配置类，用于指定模型的额外选项。

        Attributes:
            extra (str): 指定模型是否允许额外的字段，值为 "allow" 表示允许。

        """

        extra = "allow"

class RunParameter(BaseModel):
    app_no: str = Field(alias="appNo")
    data: RunData = Field(description="执行参数，执行组件时候会进行应用")
