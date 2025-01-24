import importlib
import inspect
from collections.abc import Iterator
from typing import TypeVar

from fastapi import APIRouter

from src.utils.logger import logger
from src.utils.response import ResponseUtil

from ..vo.request import RunParameter
from .dto.agent_dto import AgentConfig, ComponentConfig, PathConverterConfig

agent_crtl = APIRouter()

T = TypeVar("T")


@agent_crtl.post("/simple-ai/run")
async def run_agent_with_config(req: RunParameter) -> str:
    """Run AI agent with specified configuration.

    This interface receives a RunParameter request object containing all necessary parameters.
    Main functionalities include:
    1. Process input data and assign query text to multiple fields
    2. Parse and execute agent configuration
    3. Return execution result

    Args:
        req (RunParameter): Object containing runtime parameters, main fields include:
            - app_no: Application ID
            - data: Input data containing query text and other information

    Returns:
        str: JSON string representation of execution result, including status code and result data

    Raises:
        Exception: If no configuration exists for the specified app_no

    """
    datas = req.data
    req.data.text = datas.query
    req.data.input = datas.query
    req.data.query_text = datas.query
    # req.data.source = datas.query
    result = await resolve_agent_config(req)
    return ResponseUtil.success(result)
    # return StreamingResponse(resolve_agent_config(req), media_type="text/event-stream")


async def resolve_agent_config(req: RunParameter) -> str | dict | list | None:
    """Get app configuration based on app_no and parse execution result.

    Args:
        req (RunParameter): Run parameter object.

    Returns:
        Union[str, dict, list, None]: Execution result, which could be string, dictionary, list or None.

    """
    agent_config = _get_agent_config(req)
    path = resolve_path(agent_config)
    converter = resolve_converter(agent_config)

    path_2_value = _resolve_path_values(path, converter, agent_config, req)
    llm = path_2_value[path[-1]]

    run_params = _build_run_params(path, path_2_value, req)
    result = llm(run_params)
    if inspect.iscoroutine(result):
        result = await result

    return _process_result(result)


def _get_agent_config(req: RunParameter) -> AgentConfig:
    """Get and validate agent configuration.

    Args:
        req (RunParameter): Run parameter object.

    Returns:
        AgentConfig: Validated agent configuration.

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
                path_2_value[member] = get_bean(
                                            component_config=component_config,
                                            # components_data=app.components_data,
                                            components_data=app.factory,
                                            all_params=path_2_value)
                continue

            if converter_config.type == "list":
                value = []
                for conver in converter_config.value.split(","):
                    value.append(
                        get_bean(get_component_config(
                            component_name=conver, 
                            components=agent_config.components),
                            # components_data=app.components_data,
                            components_data=app.factory,
                            all_params=path_2_value
                            )
                    )
                path_2_value[member] = value
            else:
                if not component_config:
                    # 没有组件配置，那就是value获取
                    value = converter_config.value
                    component_config = get_component_config(component_name=value, components=agent_config.components)

                path_2_value[member] = get_bean(component_config=component_config, 
                                                        #  components_data=app.components_data, 
                                                         components_data=app.factory, 
                                                         all_params=path_2_value,
                                                         return_instance=converter_config.type == "instance")

    return path_2_value


def _build_run_params(path: list[str], path_2_value: dict, req: RunParameter) -> dict:
    """Build run parameters.

    Args:
        path (list[str]): Path list.
        path_2_value (dict): Mapping from path to value.
        req (RunParameter): Run parameter object.

    Returns:
        dict: Run parameters.

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
    """Process execution result.

    Args:
        result (Union[Iterator[T], T]): Execution result, can be an iterator or any other type.

    Returns:
        Optional[T]: Processed result, returns the first element if it's an iterator, otherwise returns the result itself.

    """
    result_text = result
    if isinstance(result, Iterator):
        result_text = ""
        for  response in result:
            if response == "DONE":
                break
            result_text = result_text+response
            
    return result_text


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
        com for com in components if com.component_name.lower() == component_name.lower()
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


def get_bean(
    component_config: ComponentConfig, components_data: dict, all_params:dict, return_instance:bool = False
) -> object|None:
    """Get the specified factory, then call the get_bean method to obtain the bean.

    Args:
        component_config (ComponentConfig): Configuration of the component.
        components_data (dict): Dictionary of available component paths.
        all_params (dict): Mapping table of component parameters for parameter resolution during component initialization.
        return_instance (bool): Whether to directly return the component instance. 
                            - If True, returns the component instance; 
                            - otherwise returns the execution result.

    Returns:
        Union[object, None]: The parsed component instance or execution result.

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

    component_path = components_data.get(component_config.name.lower())
    if not component_path:
        raise Exception(f"Not exist component name:{component_config.name}")
    module_name, class_name = component_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
     # 获取类
    component_class = getattr(module, class_name)
    
    bean = component_class().get_component(param)
    if return_instance:
        return bean
    
    return bean(param)


def resolve_component(
    component_config: ComponentConfig, components_data: dict, all_params:dict, return_instance:bool = False
) -> object | None:
    """Parse components based on component configuration, component data and request parameters.

    Args:
        component_config (ComponentConfig): Configuration of the component.
        components_data (dict): Dictionary of available component paths.
        all_params (dict): Mapping table of component parameters for parameter resolution during component initialization.
        return_instance (bool): Whether to directly return the component instance. 
                                If True, returns the component instance; otherwise returns the execution result.

    Returns:
        Union[object, None]: The parsed component instance or execution result.

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
    component_path = components_data.get(component_config.component_name.lower())
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
    
    instance = class_(**params)
    # if return_instance:
    #     return instance

    # if isinstance(instance, AbsLLMModel):
    if "model_components.model" in component_path or return_instance:
        # 模型的调用就是执行结果了
        return instance
    else:
        return instance(all_params)


@agent_crtl.post("/simple-ai/test")
def test() -> None:
    """Test interface for verifying model functionality.

    This interface creates an OpenAiStyleModel instance and calls its embeddings.create method for testing.
    The returned result will be processed based on its type: 
        - if it's an iterator, results will be returned one by one; 
        - otherwise, the result will be returned directly.
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

    from ..components.model.embedding import (
        BaseLLMParameter,
        OpenAiStyleEmbeddings,
    )
    from ..components.store.chroma_vector_store import (
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
