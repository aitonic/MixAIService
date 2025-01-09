
from pydantic import BaseModel, Field


class ComponentConfig(BaseModel):
    name: str = Field(description="组件名，不区分大小写")
    param: Optional[dict] = Field(
        default={},
        description="初始化该组件，调用__init__时候的入参，参数名和具体配置的映射(只有一个入参)"
    )


class PathConverterConfig(BaseModel):
    name: str = Field(description="执行路径中的参数名称")
    type: str = Field(description="参数类型, list-列表，instance-实例，str-字符串")
    value: str = Field(
        description="值来源，如果在组件中找不到，就直接使用该值作为实际值，如果找得到组件，是使用组件执行结果作为值"
    )


class AgentConfig(BaseModel):
    excute_path: str = Field(description="执行路径")
    converter: list[PathConverterConfig] | None = Field(description="路径参数解析配置")
    components: list[ComponentConfig] = Field(description="路径使用到的组件实例化配置")
