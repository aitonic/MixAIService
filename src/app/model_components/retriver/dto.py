from pydantic import BaseModel, Field

class MatchInfo(BaseModel):
    content:str = Field(description="检索到的内容")
    score:float = Field(description="相似度/符合度")

class RetriverResult(BaseModel):
    query:str = Field(description="检索的问题")
    results:list[MatchInfo] = Field(default=[], description="检索结果")