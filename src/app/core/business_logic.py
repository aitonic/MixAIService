import importlib
import importlib.util
import inspect
import os
import sys
import traceback

import yaml

from src.app.model_components.base_component import BaseFactory
from src.utils.logger import logger

exclude_name = ["datetime", "Undefined", "Path"]


def load_classes_from_components() -> dict[str, str]:
    """Load all classes from components directory and return a dictionary of class paths.

    Returns:
        Dict[str, str]: A dictionary where keys are lowercase class names and values are full module paths.

    """
    # components_path = os.path.join(os.path.dirname(__file__), "../model_components")
    components_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../model_components")
    )
    logger.info(f"components_path: {components_path}")

    # Add components directory to module search path
    sys.path.append(os.path.dirname(components_path))

    classes_dict = {}

    # Traverse the components directory and its subdirectories
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


def load_app_config() -> dict | list | None:
    """Load app configuration file.

    Returns:
        Union[dict, list, None]: Parsed YAML data.

    """
    with open("config/app_config.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_agent_config() -> dict | list | None:
    """Load agent configuration file.

    Returns:
        Union[dict, list, None]: Parsed YAML data.

    """
    with open("config/agent_config.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_factories() -> dict[str, str]:
    """Load all classes that implement BaseFactory from the model_components directory and return a dictionary of class paths.

    Returns:
        Dict[str, str]: A dictionary where keys are lowercase class names and values are full module paths.

    """
    components_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../model_components")
    )
    logger.info(f"components_path: {components_path}")

    # Add components directory to module search path
    sys.path.append(os.path.dirname(components_path))

    # Dictionary to store class names and module paths
    classes_dict = {}

    # Traverse components directory and its subdirectories
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

                # Skip base_component modules
                if "base_component" in full_module_name:
                    continue

                # Dynamically import the module
                module = importlib.import_module(full_module_name)

                # Get classes from module and filter those implementing BaseFactory
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)  # Only process classes
                        and issubclass(attr, BaseFactory)  # Check if subclass of BaseFactory
                        and attr is not BaseFactory  # Exclude BaseFactory itself
                    ):
                        classes_dict[attr_name.lower()] = f"{full_module_name}.{attr_name}"

            except Exception:
                logger.warning(f"Error loading component: {traceback.format_exc()}")

    return classes_dict


def get_classes_from_file(file_path: str) -> list[type]:
    """Load all classes from a specified file.
    
    Args:
        file_path (str): Path to the Python file to load classes from.
        
    Returns:
        list[type]: List of all classes defined in the file.

    """
    # Dynamically load the module
    module_name = file_path.replace("/", ".").replace("\\", ".").rsplit(".", 1)[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get all classes from the file
    classes = []
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module_name:  # Filter out imported classes, keep only locally defined ones
            classes.append(obj)
    return classes


def filter_subclasses(base_class: type, classes: list[type]) -> list[type]:
    """Filter subclasses of a specified base class.
    
    Args:
        base_class: The base class to filter subclasses from
        classes: List of all classes to filter from
    Returns:
        List of classes that are subclasses of the specified base class

    """
    return [cls for cls in classes if issubclass(cls, base_class) and cls != base_class]


# Example usage
# if __name__ == "__main__":
#     # Replace with your file path
#     file_path = "path/to/your/file.py"

#     # Get all classes
#     classes = get_classes_from_file(file_path)

#     # Filter subclasses of BaseFactory
#     subclasses = filter_subclasses(BaseFactory, classes)

#     # Print results
#     print("Subclasses of BaseFactory:")
#     for subclass in subclasses:
#         print(f"- {subclass.__name__}")
