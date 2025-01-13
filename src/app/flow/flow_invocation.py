import importlib
import inspect
from collections.abc import Iterator
from typing import TypeVar

from fastapi import APIRouter

from src.utils.logger import logger
from src.utils.response import ResponseUtil

from ..vo.request import RunParameter
from .dto.agent_dto import AgentConfig, ComponentConfig, PathConverterConfig

run_crtl = APIRouter()

T = TypeVar("T")


@run_crtl.post("/simple-ai/run")
def run_app_with_config(req: RunParameter) -> str:
    
    datas = req.data
    req.data.text = datas.query
    req.data.input = datas.query
    req.data.query_text = datas.query
    # req.data.source = datas.query
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
    logger.info(f"{req.app_no} 的配置信息：{agent_config}")
    return AgentConfig(**agent_config)


def _resolve_path_values(path: list[str], converter: dict[str, PathConverterConfig], agent_config: AgentConfig, req: RunParameter) -> dict:
    """Parse the path and generate corresponding values.

    Args:
        path (list[str]): List of paths.
        converter (dict[str, PathConverterConfig]): Path converter configuration.
        agent_config (AgentConfig): Agent configuration.
        req (RunParameter): Run parameter object.

    Returns:
        dict: Mapping from path to value.

    """
    from src.main import app
    path_2_value = {}
    path_2_value.update(req.data.model_dump(exclude_none=True))
    for param in path:
        members = param.split(",")
        for member in members:
            component_config = get_component_config(member, agent_config.components)
            converter_config = converter.get(member)
            if not converter_config:
                path_2_value[member] = resolve_component(
                                            component_config=component_config,
                                            components_data=app.components_data,
                                            all_params=path_2_value)
                continue

            if converter_config.type == "list":
                value = []
                for conver in converter_config.value.split(","):
                    value.append(
                        resolve_component(get_component_config(
                            component_name=conver, 
                            components=agent_config.components),
                            components_data=app.components_data,
                            all_params=path_2_value
                            )
                    )
                path_2_value[member] = value
            else:
                if not component_config:
                    # 没有组件配置，那就是value获取
                    value = converter_config.value
                    component_config = get_component_config(component_name=value, components=agent_config.components)

                path_2_value[member] = resolve_component(component_config=component_config, 
                                                         components_data=app.components_data, 
                                                         all_params=path_2_value,
                                                         return_instance=converter_config.type == "instance")

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
                [p.as_parameter() for p in param] if isinstance(param, list) else param.as_parameter()
            )
    run_params.update(req.data.model_dump(exclude_none=True))
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
    if agent_config.converter:
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
    component_config: ComponentConfig, components_data: dict, all_params:dict, return_instance:bool = False
) -> object | None:
    """根据组件配置、组件数据和请求参数解析组件。

    Args:
        component_config (ComponentConfig): 组件的配置。
        components_data (dict): 可用组件的路径字典。
        all_params (dict): 组件参数的映射表，用于初始化组件时的参数解析。
        return_instance (bool): 是否直接返回组件实例。如果为 True，返回组件实例；否则返回执行结果。

    Returns:
        Union[object, None]: 解析得到的组件实例或执行结果。

    """
    # 进行实例化，目前的涉及是，每个类的实例化，只支持一个对象入参
    param: dict = component_config.param
    if not param:
        param = {}
    # 接口入参替换
    for _, val in param.items():
        if isinstance(val, dict):
            val.update(all_params)
    param.update(all_params)

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

    params = {}
    for name, parameter in init_params.items():
        if name == "self":
            continue
        if parameter.annotation is not str:
            p = param[name]
            if isinstance(p, dict):
                params[name] = parameter.annotation(**p)
            else:
                params[name] = p
        else:
            params[name] = param[name]


    # params = {
    #     name: parameter.annotation(**param[name])
    #     if parameter.annotation is not str
    #     else param[name]
    #     for name, parameter in init_params.items()
    #     if name != "self"
    # }
    
    instance = class_(**params)
    # if return_instance:
    #     return instance

    # if isinstance(instance, AbsLLMModel):
    if "model_components.model" in component_path or return_instance:
        # 模型的调用就是执行结果了
        return instance
    else:
        return instance(all_params)




@run_crtl.post("/simple-ai/test")
def test() -> None:
    """测试接口，用于验证模型的功能。

    该接口创建一个 OpenAiStyleModel 实例，并调用其 embeddings.create 方法进行测试。
    返回的结果将根据其类型进行处理，如果是迭代器，则逐个返回结果；否则直接返回结果。
    """
    # from src.app.model_components.model.openai_style import (
    #     OpenAiStyleLLMParameter,
    #     OpenAiStyleModel,
    #     BaseCompletionParameter
    # )

    # result = OpenAiStyleModel(OpenAiStyleLLMParameter(api_key = "123", full_url = "http://127.0.0.1:1234/v1/chat/completions")).chat.completions.create(BaseCompletionParameter(stream=True,messages=[{"role":"system", "content":"你是一个数学家"}, {"role":"user","content":"10的20倍是多少"}]))
    # # result = OpenAiStyleModel(OpenAiStyleLLMParameter(api_key = "123", base_url = "http://192.168.11.11:8070")).chat.completions.create(text="这是一个测试", )

    # if isinstance(result, Iterator):
    #     for r in result:
    #         return r
    # else:
    #     return result

    # from openai import OpenAI
    # response = OpenAI(base_url = "http://127.0.0.1:1234/v1", timeout=30, max_retries = 3, api_key="1234").chat.completions.create(model = "qwen",stream=True, messages=[{"role":"system", "content":"你是一个数学家"}, {"role":"user","content":"10的20倍是多少"}])
    
    # # for r in response:
    # #     print(r)

    # # from fastapi.responses import StreamingResponse
    # # return StreamingResponse(response, media_type="text/event-stream")
    # for r in response.response.iter_lines():
    #     if "DONE" in r:
    #         return
    #     yield r

    from ..model_components.model.embedding import (
        BaseLLMParameter,
        OpenAiStyleEmbeddings,
    )
    from ..model_components.store.chroma_vector_store import (
        ChromaVectorStore,
        VectorQueryParameter,
    )

    client = ChromaVectorStore.create_client()
    
    # 新增
    # collection_name = "test-collection"
    # client.create_collection(collection_name)
    # client.add_text(text="测试文本embedding", collection_name=collection_name, embed_function=OpenAiStyleEmbeddings(BaseLLMParameter(api_key="1234", base_url="http://127.0.0.1:1234")))
    result = client.query(VectorQueryParameter(
        query_text="于谦", 
        embed_function=OpenAiStyleEmbeddings(BaseLLMParameter(api_key="1234", 
                                                              base_url="http://192.168.11.11:8070"
                                                              )
                                             )
                                            )
                          )

    return result
