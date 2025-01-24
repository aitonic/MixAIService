from pydantic import BaseModel, Field


class MatchInfo(BaseModel):
    content:str = Field(description="检索到的内容")
    score:float = Field(description="相似度/符合度")

class RetriverResult(BaseModel):
    query:str = Field(description="检索的问题")
    results:list[MatchInfo] = Field(default=[], description="检索结果")


class RetriverQuery(BaseModel):
    query:str = Field(description="检索的问题")
    top_k:int = Field(default=5, description="返回结果的最大数量")
    search_keys:list[str] = Field(default=5, description="查询key列表/search_collections")
    meta_data:dict = Field(default={}, description="其他过滤条件， and关系")
    score:float = Field(default=0.4, description="相似度/符合度阈值")
