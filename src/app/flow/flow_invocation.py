import importlib
import inspect
from collections.abc import Iterator
from typing import TypeVar

# from model_components.model.base import AbsLLMModel
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.utils.logger import logger

# from src.utils.Response import ResponseUtil
from src.utils.response import ResponseUtil

run_crtl = APIRouter()

T = TypeVar("T")

class ComponentConfig(BaseModel):
    name: str = Field(description="组件名，不区分大小写")
    param: dict = Field(
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
    converter: list[PathConverterConfig] = Field(description="路径参数解析配置")
    components: list[ComponentConfig] = Field(description="路径使用到的组件实例化配置")


class RunParameter(BaseModel):
    app_no: str = Field(alias="appNo")
    data: dict


@run_crtl.post("/simple-ai/v1/run")
def run_app_with_config_v1(req: RunParameter) -> str:
    from src.main import app

    config = app.app_config.get(req.app_no)
    if not config:
        return {"error": "Invalid app_no"}

    logger.info(config)

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
    class_name: str, components: list[dict], components_data: dict[str, str], req: RunParameter
) -> T:
    """解析类名并实例化类对象。

    Args:
        class_name (str): 要解析的类名。
        components (list[dict]): 组件列表。
        components_data (dict[str, str]): 组件路径数据。
        req (RunParameter): 运行参数对象。

    Returns:
        T: 实例化的类对象或类对象的执行结果。

    """
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
        if parameter.annotation is not str  # 直接比较类型
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


@run_crtl.post("/simple-ai/run")
def run_app_with_config(req: RunParameter) -> str:
    
    result = _resolve_app_config(req)
    return ResponseUtil.success(result)



def _resolve_app_config(req: RunParameter) -> str | dict | list | None:
    """根据 app_no 获取 app 配置并解析执行结果。

    Args:
        req (RunParameter): 运行参数对象。

    Returns:
        Union[str, dict, list, None]: 执行结果，可能是字符串、字典、列表或 None。

    """
    agent_config = _get_agent_config(req)
    path = resolve_path(agent_config)
    converter = resolve_converter(agent_config)

    path_2_value = _resolve_path_values(path, converter, agent_config, req)
    llm = path_2_value[path[-1]]

    run_params = _build_run_params(path, path_2_value, req)
    result = llm(run_params)

    return _process_result(result)


def _get_agent_config(req: RunParameter) -> AgentConfig:
    """获取并验证 agent 配置。

    Args:
        req (RunParameter): 运行参数对象。

    Returns:
        AgentConfig: 验证后的 agent 配置。

    """
    from src.main import app
    agent_config = app.agent_config.get(req.app_no)
    if not agent_config:
        raise Exception(f"不存在 app 配置：{req.app_no}")
    logger.error(f"{req.app_no} 的配置信息：{agent_config}")
    return AgentConfig(**agent_config)


def _resolve_path_values(path: list[str], converter: dict[str, PathConverterConfig], agent_config: AgentConfig, req: RunParameter) -> dict:
    """解析路径并生成对应的值。

    Args:
        path (list[str]): 路径列表。
        converter (dict[str, PathConverterConfig]): 路径转换器配置。
        agent_config (AgentConfig): Agent 配置。
        req (RunParameter): 运行参数对象。

    Returns:
        dict: 路径到值的映射。

    """
    from src.main import app
    path_2_value = {}
    for param in path:
        members = param.split(",")
        for member in members:
            component_config = get_component_config(member, agent_config.components)
            converter_config = converter.get(member)
            if converter_config is None:
                path_2_value[member] = resolve_component(component_config, app.components_data, req)
                continue

            if converter_config.type == "list":
                value = []
                for conver in converter_config.value.split(","):
                    value.append(
                        resolve_component(get_component_config(conver, agent_config.components), app.components_data, req)
                    )
                path_2_value[member] = value
            else:
                path_2_value[member] = resolve_component(component_config, app.components_data, req)

    return path_2_value


def _build_run_params(path: list[str], path_2_value: dict, req: RunParameter) -> dict:
    """构建运行参数。

    Args:
        path (list[str]): 路径列表。
        path_2_value (dict): 路径到值的映射。
        req (RunParameter): 运行参数对象。

    Returns:
        dict: 运行参数。

    """
    run_params = {}
    if len(path) > 1:
        param_names = path[-2].split(",")
        for pa in param_names:
            param = path_2_value[pa]
            run_params[pa] = (
                [p.as_param() for p in param] if isinstance(param, list) else param.as_param()
            )
    run_params.update(req.data)
    return run_params


  # 泛型，用于匹配输入和输出类型

def _process_result(result: Iterator[T] | T) -> T | None:
    """处理执行结果。

    Args:
        result (Union[Iterator[T], T]): 执行结果，可以是迭代器或其他任意类型。

    Returns:
        Optional[T]: 处理后的结果，如果是迭代器则返回其第一个元素，否则返回结果本身。

    """
    if isinstance(result, Iterator):
        return next(result, None)  # 返回迭代器的第一个元素或 None
    return result


def resolve_path(agent_config: AgentConfig) -> list[str]:
    # 切割成顺序列表
    return agent_config.excute_path.split("-")


def resolve_converter(agent_config: AgentConfig) -> dict:
    # 生成name->config的映射
    converter_mapping = {}
    for converter in agent_config.converter:
        converter_mapping[converter.name] = converter
    return converter_mapping


def get_component_config(
    component_name: str, components: list[ComponentConfig]
) -> ComponentConfig:
    filter_result = [
        com for com in components if com.name.lower() == component_name.lower()
    ]
    if not filter_result:
        return None

    return filter_result[0]


def get_converter_config(
    converter_name: str, converters: list[PathConverterConfig]
) -> PathConverterConfig:
    filter_result = [
        com for com in converters if com.name.lower() == converter_name.lower()
    ]
    if not filter_result:
        return None

    return filter_result[0]


def resolve_component(
    component_config: ComponentConfig, components_data: dict, req: RunParameter
) -> object | dict | list | str | int | float | None:
    """根据组件配置、组件数据和请求参数解析组件。

    Args:
        component_config (ComponentConfig): 组件的配置。
        components_data (dict): 可用组件的路径字典。
        req (RunParameter): 运行参数。

    Returns:
        Union[object, dict, list, str, int, float, None]:
        解析得到的组件实例或执行结果。

    """
    # 进行实例化，目前的涉及是，每个类的实例化，只支持一个对象入参
    param: dict = component_config.param
    if not param:
        param = {}
    # 接口入参替换
    param.update(req.data)
    # 前一个直接关联的组件执行结果的替换
    # TODO
    # 通过指定的类名字符串，获取类对象
    # class_path = app.components_data[component_class]
    component_path = components_data.get(component_config.name.lower())
    module_name, class_name = component_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    # 获取类的 __init__ 方法的参数
    init_signature = inspect.signature(class_.__init__)
    init_params = init_signature.parameters

    params = {
        name: parameter.annotation(**param[name])
        if parameter.annotation is not str
        else param[name]
        for name, parameter in init_params.items()
        if name != "self"
    }
    
    instance = class_(**params)

    # if isinstance(instance, AbsLLMModel):
    if "model_components.model" in component_path:
        # 模型的调用就是执行结果了
        return instance
    else:
        return instance(req.data)
