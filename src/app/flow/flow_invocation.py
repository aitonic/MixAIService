import importlib
import inspect
from collections.abc import Iterator

# from model_components.model.base import AbsLLMModel
from fastapi import APIRouter
# from src.utils.Response import ResponseUtil
from utils.Response import ResponseUtil
run_crtl = APIRouter()

class ComponentConfig(BaseModel):
    name:str = Field(description="组件名，不区分大小写")
    param:dict = Field(description="初始化该组件，调用__init__时候的入参，参数名和具体配置的映射(只有一个入参)")

class PathConverterConfig(BaseModel):
    name:str = Field(description="执行路径中的参数名称")
    type:str = Field(description="参数类型, list-列表，instance-实例，str-字符串")
    value:str = Field(description="值来源，如果在组件中找不到，就直接使用该值作为实际值，如果找得到组件，是使用组件执行结果作为值")

class AgentConfig(BaseModel):
    excute_path:str = Field(description="执行路径")
    converter:list[PathConverterConfig] = Field(description="路径参数解析配置")
    components:list[ComponentConfig] = Field(description="路径使用到的组件实例化配置")

class RunParameter(BaseModel):
    app_no: str = Field(alias="appNo")
    data: dict


@run_crtl.post('/simple-ai/v1/run')
def run_app_with_config(req:RunParameter) -> str:
    from main import app
    config = app.app_config.get(req.app_no)
    if not config:
        return {"error": "Invalid app_no"}

    print(config)

    # 获取app的组合
    compose = config["compose"]
    # 根据短线切割，得到所有的类
    class_names: list[str] = compose["path"].split("-")
    components: list[str] = compose["components"]

    class_2_instance = {}
    run_instance = None
    run_param_index = len(class_names) - 2
    index_2_param_name = {}
    index_2_instance = {}
    # 逐个类的解析
    for index, class_name in enumerate(class_names):
        # 此处的class_name可能是多个类名的拼接，统一入参
        param_definition = []
        param_name = None
        if "=" in class_name:
            param_definition = class_name.split("=")
            param_name = param_definition[0]
            names = param_definition[1].split("+")
        else:
            names = class_name.split("+")
        if len(names) > 1:
            # 此处的实例就是列表
            instances = []
            for name in names:
                class_2_instance[name] = resolve_class(
                    name, components, app.components_data, req
                )
                instances.append(class_2_instance[name].__dict__)
            index_2_instance[index] = instances
            index_2_param_name[index] = param_name
        else:
            class_2_instance[class_name] = resolve_class(
                class_name, components, app.components_data, req
            )
            index_2_instance[index] = class_2_instance[class_name]

        if index == len(class_names) - 1:
            run_instance = class_2_instance[class_name]

    # 调用需要执行的实例，得到结果
    # 取实例执行的参数
    run_params = index_2_instance[run_param_index]
    run_param_name = index_2_param_name[run_param_index]
    if run_param_name:
        result = run_instance({run_param_name: run_params})
    else:
        result = run_instance(run_params)

    if isinstance(result, Iterator):
        for r in result:
            return ResponseUtil.success(r)

    return ResponseUtil.success(result)


def resolve_class(
    class_name: str, components: list[str], components_data: dict, req: RunParameter
):
    # 从 components_data 中获取类
    component_path = components_data.get(class_name.lower())
    if not component_path:
        raise Exception(f"Class not found in components_data:{class_name}")

    # 找到组件
    component = [
        component
        for component in components
        if component["name"].lower() == class_name.lower()
    ]
    if not component:
        raise Exception(f"不存在组件类：{class_name}的相关配置")

    # 进行实例化，目前的涉及是，每个类的实例化，只支持一个对象入参
    param: dict = component[0]["param"]
    if not param:
        param = {}
    # 接口入参替换
    param.update(req.data)
    # 前一个直接关联的组件执行结果的替换
    # TODO
    # 通过指定的类名字符串，获取类对象
    # class_path = app.components_data[component_class]
    module_name, class_name = component_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    # 获取类的 __init__ 方法的参数
    init_signature = inspect.signature(class_.__init__)
    init_params = init_signature.parameters
    # print(init_params)  # 打印 __init__ 方法的参数
    # for name, parameter in init_params.items():
    #     print(parameter.annotation)
    #     print(parameter.annotation == str)
    # params = {name: parameter.annotation(**param[name]) if parameter.annotation != str else param[name] for name, parameter in init_params.items() if name != 'self'}
    params = {
        name: parameter.annotation(**param[name])
        if parameter.annotation != str  # 直接比较类型
        else param[name]
        for name, parameter in init_params.items()
        if name != "self"
    }
    instance = class_(**params)
    # print(instance.__dict__)

        # if isinstance(instance, AbsLLMModel):
        if "model_components.model" in component_path:
            # 模型的调用就是执行结果了
            return instance
        else:
            return instance(req.data)
        

@run_crtl.post('/simple-ai/v2/run')
def run_app_with_config(req:RunParameter) -> str:
    result = resolve_app_config(req)
    return ResponseUtil.success(result)
    
    # if isinstance(result, Iterator):
    #     for r in result:
    #         return ResponseUtil.success(r)

    # return ResponseUtil.success(result)

def resolve_app_config(req:RunParameter):
    # 根据app_no获取app配置
    from main import app
    # config = app.app_config.get(req.app_no)

    # 根据app配置，取出所有的agent配置
    # TODO 先认为是一对一的关系
    agent_config = app.agent_config.get(req.app_no)
    if not agent_config:
        raise Exception(f"不存在app配置：{req.app_no}")
    
    agent_config = AgentConfig(**agent_config)

    path:list[str] = resolve_path(agent_config)
    converter:dict[str, PathConverterConfig] = resolve_converter(agent_config)
    # 由于参数是进行传递的，应该根据顺序进行解析
    path_2_value = {}
    for param in path:
        members = param.split(",")
        for member in members:
            value = None
            component_config = get_component_config(member, agent_config.components)
            converter_config = converter.get(member)
            if not converter_config:
                # 直接从组件中实例化
                value = resolve_component(component_config, app.components_data, req)
                path_2_value[member] = value
                continue
            
            if converter_config.type == "list":
                # 切割成列表
                value = []
                comverter_configs = converter_config.value.split(",")
                for conver in comverter_configs:
                    # 解析component
                    path_2_value[conver] = resolve_component(get_component_config(conver, agent_config.components), app.components_data, req)
                    value.append(path_2_value[conver])
            else:
                # 直接从组件中实例化
                value = resolve_component(component_config, app.components_data, req)
                
            path_2_value[member] = value
    
    # 执行最终的agent执行器(模型调用)
    llm = path_2_value[path[-1]]
    # 取执行参数
    run_params = {}
    if len(path) > 1:
        param_names = path[len(path)-2].split(",")
        for pa in param_names:
            param = path_2_value[pa]
            pp = None
            if isinstance(param, list):
                pp = []
                for p in param:
                    pp.append(p.as_param())
            else:
                pp = param.as_param()
            run_params[pa] = pp

    run_params.update(req.data)
    # 执行
    result = llm(run_params)
    if isinstance(result, Iterator):
        for r in result:
            return r

    return result

def resolve_path(agent_config:AgentConfig)->list[str]:
    # 切割成顺序列表
    return agent_config.excute_path.split("-")

def resolve_converter(agent_config:AgentConfig) -> dict:
    # 生成name->config的映射
    converter_mapping = {}
    for converter in agent_config.converter:
        converter_mapping[converter.name] = converter
    return converter_mapping

def get_component_config(component_name:str, components:list[ComponentConfig]) -> ComponentConfig:
    filter_result = [com for com in components if com.name.lower() == component_name.lower()]
    if not filter_result:
        return None
    
    return filter_result[0]

def get_converter_config(converter_name:str, converters:list[PathConverterConfig]) -> PathConverterConfig:
    filter_result = [com for com in converters if com.name.lower() == converter_name.lower()]
    if not filter_result:
        return None
    
    return filter_result[0]

def resolve_component(component_config:ComponentConfig, components_data:dict, req:RunParameter):
    
    # 进行实例化，目前的涉及是，每个类的实例化，只支持一个对象入参
    param:dict = component_config.param
    if not param:
        param = {}
    # 接口入参替换
    param.update(req.data)
    # 前一个直接关联的组件执行结果的替换
    # TODO
    # 通过指定的类名字符串，获取类对象
    # class_path = app.components_data[component_class]
    component_path = components_data.get(component_config.name.lower())
    module_name, class_name = component_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    # 获取类的 __init__ 方法的参数
    init_signature = inspect.signature(class_.__init__)
    init_params = init_signature.parameters

    params = {name: parameter.annotation(**param[name]) if parameter.annotation != str else param[name] for name, parameter in init_params.items() if name != 'self'}
    instance = class_(**params)

    # if isinstance(instance, AbsLLMModel):
    if "model_components.model" in component_path:
        # 模型的调用就是执行结果了
        return instance
    else:
        return instance(req.data)
