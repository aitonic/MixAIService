from pydantic import BaseModel, Field

class RunParameter(BaseModel):
    app_no: str = Field(alias="appNo")
    data: dict