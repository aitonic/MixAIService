from pydantic import BaseModel, Field
import importlib
import inspect
from typing import Iterator
from ..model_components.model.base import AbsLLMModel
# from model_components.model.base import AbsLLMModel
from fastapi import APIRouter
from utils.Response import ResponseUtil
run_crtl = APIRouter()

# class VariableModel(BaseModel):

#     class Config:
#         # extra = Extra.allow  # 允许额外字段
#         extra='allow'
    
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)  # 调用父类的构造函数
#         for name, value in kwargs.items():
#             self.__setattr__(name, value)

class RunParameter(BaseModel):
    app_no: str = Field(alias="appNo")
    data: dict


@run_crtl.post('/simple-ai/run')
def run_app_with_config(req:RunParameter) -> str:
    from src.main import app
    config = app.app_config.get(req.app_no)
    if not config:
        return {"error": "Invalid app_no"}
    
    print(config)

    # 获取app的组合
    compose = config["compose"]
    # 根据短线切割，得到所有的类
    class_names:list[str] = compose["path"].split("-")
    components:list[str] = compose["components"]

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
                class_2_instance[name] = resolve_class(name, components, app.components_data, req)
                instances.append(class_2_instance[name].__dict__)
            index_2_instance[index] = instances
            index_2_param_name[index] = param_name
        else:
            class_2_instance[class_name] = resolve_class(class_name, components, app.components_data, req)
            index_2_instance[index] = class_2_instance[class_name]

        if index == len(class_names) - 1:
            run_instance = class_2_instance[class_name]

    # 调用需要执行的实例，得到结果
    # 取实例执行的参数
    run_params = index_2_instance[run_param_index]
    run_param_name = index_2_param_name[run_param_index]
    if run_param_name:
        result = run_instance({run_param_name:run_params})
    else:
        result = run_instance(run_params)
    
    if isinstance(result, Iterator):
        for r in result:
            return ResponseUtil.success(r)

    return ResponseUtil.success(result)


def resolve_class(class_name:str, components:list[str], components_data:dict, req:RunParameter):
    # 从 components_data 中获取类
        component_path = components_data.get(class_name.lower())
        if not component_path:
            raise Exception(f"Class not found in components_data:{class_name}")
        
        # 找到组件
        component = [component for component in components if component["name"].lower() == class_name.lower()]
        if not component:
            raise Exception(f"不存在组件类：{class_name}的相关配置")
        
        # 进行实例化，目前的涉及是，每个类的实例化，只支持一个对象入参
        param:dict = component[0]["param"]
        if not param:
            param = {}
        # 接口入参替换
        param.update(req.data)
        # 前一个直接关联的组件执行结果的替换
        # TODO
        # 通过指定的类名字符串，获取类对象
        # class_path = app.components_data[component_class]
        module_name, class_name = component_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        # 获取类的 __init__ 方法的参数
        init_signature = inspect.signature(class_.__init__)
        init_params = init_signature.parameters
        # print(init_params)  # 打印 __init__ 方法的参数
        # for name, parameter in init_params.items():
        #     print(parameter.annotation)
        #     print(parameter.annotation == str)
        params = {name: parameter.annotation(**param[name]) if parameter.annotation != str else param[name] for name, parameter in init_params.items() if name != 'self'}
        instance = class_(**params)
        # print(instance.__dict__)

        # if isinstance(instance, AbsLLMModel):
        if "model_components.model" in component_path:
            # 模型的调用就是执行结果了
            return instance
        else:
            return instance(req.data)