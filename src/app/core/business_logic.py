import importlib
import os
import sys

import yaml

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
    print(f"components_path: {components_path}")

    # 将 components 目录添加到模块搜索路径
    sys.path.append(os.path.dirname(components_path))

    classes_dict = {}

    # 遍历 components 目录及其子目录
    for root, _, files in os.walk(components_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_name = os.path.splitext(file)[0]
                module_path = os.path.relpath(root, components_path).replace(
                    os.sep, "."
                )
                full_module_name = (
                    f"model_components.{module_path}.{module_name}"
                    if module_path
                    else f"model_components.{module_name}"
                )

                # logger.info(f"Importing module: {full_module_name}")  # 调试信息
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
                            # 加载类尝试一下
                            # importlib.import_module(classes_dict[attr_name])

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
