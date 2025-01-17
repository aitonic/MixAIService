from ..base_component import BaseComponent, BaseFactory
from .prompt import HumanPrompt, SystemPrompt


class PromtFactory(BaseFactory):

    def get_bean(self, param: dict) -> BaseComponent:
        component_type = param["component_type"]
        if component_type == "system":
            return SystemPrompt(param["system_prompt"])
        elif component_type == "human":
            return HumanPrompt(param["human_message"])
        else:
            raise Exception(f"Unimplemented prompt component_type :{component_type}")
