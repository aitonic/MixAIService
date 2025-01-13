from  pydantic import BaseModel

class Source(BaseModel):
    source: str | bytes