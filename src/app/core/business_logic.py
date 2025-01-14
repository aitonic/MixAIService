import importlib
import os
import sys
import traceback

import yaml

from src.app.model_components.base_component import BaseFactory
from src.utils.logger import logger

exclude_name = ["datetime", "Undefined", "Path"]


def load_classes_from_components() -> dict[str, str]:
    """加载 components 目录中的所有类并返回类路径字典。

    Returns:
        Dict[str, str]: 一个字典，键是类名的小写形式，值是完整的模块路径。

    """
    # components_path = os.path.join(os.path.dirname(__file__), "../model_components")
    components_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../model_components")
    )
    logger.info(f"components_path: {components_path}")

    # 将 components 目录添加到模块搜索路径
    sys.path.append(os.path.dirname(components_path))

    classes_dict = {}

    # 遍历 components 目录及其子目录
    for root, _, files in os.walk(components_path):
        for file in files:
            if not file.endswith(".py") or file == "__init__.py":
                continue

            try:
                module_name = os.path.splitext(file)[0]
                module_path = os.path.relpath(root, components_path).replace(
                    os.sep, "."
                )
                full_module_name = (
                    f"model_components.{module_path}.{module_name}"
                    if module_path
                    else f"model_components.{module_name}"
                )

                if "base_component" in full_module_name:
                    continue
                # logger.info(f"Importing module, module_name: {module_name}, module_path:{module_path}, full_module_name:{full_module_name}")  # 调试信息
                module = importlib.import_module(full_module_name)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                            isinstance(attr, type)
                            and attr_name != "ABC"
                            and not attr_name.startswith("Abs")
                            and attr_name not in exclude_name
                        ):
                            classes_dict[attr_name.lower()] = f"{full_module_name}.{attr_name}"
            except Exception:
                logger.warn(f"组件导入出错：{traceback.format_exc()}")


    return classes_dict


# 加载app配置文件
def load_app_config() -> dict | list | None:
    """加载 app 配置文件。

    Returns:
        Union[dict, list, None]: 解析后的 YAML 数据。

    """
    with open("config/app_config.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)



def load_agent_config() -> dict | list | None:
    """加载 agent 配置文件。

    Returns:
        Union[dict, list, None]: 解析后的 YAML 数据。

    """
    with open("config/agent_config.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)



def load_factories() -> dict[str, str]:
    """加载 model_components 目录中的所有实现了 BaseFactory 的类，并返回类路径字典。

    Returns:
        Dict[str, str]: 一个字典，键是类名的小写形式，值是完整的模块路径。
    """

    # from src.app.model_components.doc_reader.doc_reader_factory import DocReaderFactory
    # from src.app.model_components.base_component import BaseFactory

    # print(issubclass(DocReaderFactory, BaseFactory))

    components_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../model_components")
    )
    logger.info(f"components_path: {components_path}")

    # 将 components 目录添加到模块搜索路径
    sys.path.append(os.path.dirname(components_path))

    # 存储类名和模块路径的字典
    classes_dict = {}

    # 遍历 components 目录及其子目录
    for root, _, files in os.walk(components_path):
        for file in files:
            if not file.endswith(".py") or file == "__init__.py":
                continue

            try:
                module_name = os.path.splitext(file)[0]
                module_path = os.path.relpath(root, components_path).replace(os.sep, ".")
                full_module_name = (
                    f"src.app.model_components.{module_path}.{module_name}"
                    if module_path
                    else f"src.app.model_components.{module_name}"
                )

                # 忽略 base_component 模块
                if "base_component" in full_module_name:
                    continue

                # 动态导入模块
                module = importlib.import_module(full_module_name)

                # 获取模块中的类并筛选实现了 BaseFactory 的类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)  # 仅处理类
                        and issubclass(attr, BaseFactory)  # 检查是否是 BaseFactory 的子类
                        and attr is not BaseFactory  # 排除 BaseFactory 本身
                    ):
                        classes_dict[attr_name.lower()] = f"{full_module_name}.{attr_name}"

            except Exception as e:
                logger.warning(f"加载组件时出错：{traceback.format_exc()}")

    return classes_dict


import inspect
import importlib.util
from typing import List, Type

def get_classes_from_file(file_path: str) -> List[Type]:
    """
    从指定文件中加载所有类。
    
    :param file_path: 文件路径
    :return: 文件中定义的所有类
    """
    # 动态加载模块
    module_name = file_path.replace("/", ".").replace("\\", ".").rsplit(".", 1)[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 获取文件中的所有类
    classes = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module_name:  # 过滤掉导入的类，仅保留本文件定义的类
            classes.append(obj)
    return classes


def filter_subclasses(base_class: Type, classes: List[Type]) -> List[Type]:
    """
    筛选指定类的子类。
    
    :param base_class: 基类
    :param classes: 所有类列表
    :return: 是指定基类的子类的类列表
    """
    return [cls for cls in classes if issubclass(cls, base_class) and cls != base_class]


# 示例用法
if __name__ == "__main__":
    # 替换为您的文件路径
    file_path = "path/to/your/file.py"

    # 获取所有类
    classes = get_classes_from_file(file_path)

    # 筛选 BaseFactory 的子类
    subclasses = filter_subclasses(BaseFactory, classes)

    # 打印结果
    print("BaseFactory 的子类有：")
    for subclass in subclasses:
        print(f"- {subclass.__name__}")
