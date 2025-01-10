from typing import Optional

from pydantic import BaseModel, Field

class RunData(BaseModel):
    query:str = Field(description="调用的数据")
    base_url:Optional[str] = Field(default = None, description="模型（completions/embeddings）的基础url，例如:http://127.0.0.1:1234")
    full_url:Optional[str] = Field(default = None, description="模型（completions/embeddings）的全路径url，当不是openai格式的地址的时候，需要指定")
    system_prompt:Optional[str] = Field(default = None, description="system message")
    search_collections:Optional[list[str]] = Field(default = None, description="vector检索的时候，可以指定检索的collection")
    collection_name:Optional[str] = Field(default = None, description="vector添加文本的时候，可以指定检索的collection")


    class Config:
        extra = "allow"

class RunParameter(BaseModel):
    app_no: str = Field(alias="appNo")
    data: RunData = Field(description="执行参数，执行组件时候会进行应用")
