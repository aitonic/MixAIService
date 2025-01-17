
from pydantic import BaseModel, Field


class ComponentConfig(BaseModel):
    name: str = Field(description="组件名，不区分大小写")
    alias: str | None = Field(default= None ,description="别名，当需要多次使用的时候，可以设置这个值")
    param: dict | None = Field(
        default={},
        description="初始化该组件，调用 __init__ 时的入参，参数名和具体配置的映射（只有一个入参）"
    )

    @property
    def component_name(self) -> str:
        if "alias" in self.__dict__ and self.alias:
            return self.alias
        
        return self.name

class PathConverterConfig(BaseModel):
    name: str = Field(description="执行路径中的参数名称")
    type: str = Field(description="参数类型, list-列表，instance-实例，str-字符串")
    value: str = Field(
        description="值来源，如果在组件中找不到，就直接使用该值作为实际值，如果找得到组件，是使用组件执行结果作为值"
    )


class AgentConfig(BaseModel):
    excute_path: str = Field(description="执行路径")
    converter: list[PathConverterConfig] | None = Field(default=[], description="路径参数解析配置")
    components: list[ComponentConfig] = Field(default=[], description="路径使用到的组件实例化配置")
