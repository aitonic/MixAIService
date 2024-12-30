import os
import importlib
import sys
import yaml
import inspect

exclude_name = ["datetime", "Undefined", "Path"]
def load_classes_from_components():
    components_path = os.path.join(os.path.dirname(__file__), '../model_components')
    print(f"components_path: {components_path}")
    
    # 将 components 目录添加到模块搜索路径
    sys.path.append(os.path.dirname(components_path))
    
    classes_dict = {}

    # 遍历 components 目录及其子目录
    for root, dirs, files in os.walk(components_path):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                module_name = os.path.splitext(file)[0]
                module_path = os.path.relpath(root, components_path).replace(os.sep, '.')
                full_module_name = f"model_components.{module_path}.{module_name}" if module_path else f"model_components.{module_name}"
                
                # print(f"Importing module: {full_module_name}")  # 调试信息
                module = importlib.import_module(full_module_name)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type):
                        # print(f"Found class: {attr_name}")  # 调试信息
                        if attr_name != "ABC" and not attr_name.startswith('Abs') and attr_name not in exclude_name:
                            classes_dict[attr_name.lower()] = f"{full_module_name}.{attr_name}"
                            # 加载类尝试一下
                            # importlib.import_module(classes_dict[attr_name])

    return classes_dict

# 加载app配置文件
def load_config():
    with open("config/app_config.yaml", 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)