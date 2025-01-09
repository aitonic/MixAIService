from collections.abc import Mapping
from typing import Any

from jinja2 import Environment, Template, meta

from .base import AbsPrompt


class BasePrompt(AbsPrompt):
    """基础的prompt类.
    
    使用jinja2作为模板处理
    """

    def __init__(self, role: str, prompt_str: str) -> None:
        super().__init__(role, prompt_str)

    def generate_prompt(self, params: dict) -> str:
        """根据参数处理prompt."""
        # 创建 Jinja2 环境
        env = Environment(autoescape=True)

        # 解析模板源代码，生成抽象语法树（AST）
        parsed_content = env.parse(self.content)

        # 提取未声明的变量名
        undeclared_variables = meta.find_undeclared_variables(parsed_content)

        if not undeclared_variables:
            # 没有需要替换的变量，直接返回
            return self

        # 校验是否所有参数都已提供
        for var in undeclared_variables:
            if var not in params:
                raise ValueError(f"Missing parameter: {var}")
        self.content = Template(self.content).render(params)
        return self

    def __call__(self, *args: tuple[object, ...], **kwds: Mapping[str, Any]) -> str: # noqa: N807
        """调用对象，生成 prompt。

        Args:
            *args: 任意类型的参数元组。
            **kwds: 键为字符串的参数映射。

        Returns:
            str: 生成的 prompt。

        """
        return self.generate_prompt(args[0])

    def as_parameter(self) -> dict:
        """返回对象的属性字典。

        Returns:
            dict: 当前对象的属性字典。

        """
        return self.__dict__


class SystemPrompt(BasePrompt):
    def __init__(self, system_prompt: str) -> None:
        super().__init__("system", system_prompt)

    def generate_prompt(self, params: dict) -> BasePrompt:
        return super().generate_prompt(params)


class HumanPrompt(BasePrompt):
    def __init__(self, human_message: str) -> None:
        super().__init__("user", human_message)

    def generate_prompt(self, params: dict) -> BasePrompt:
        return super().generate_prompt(params)
