from ..base_component import (
    BaseFactory,
    BaseComponent
)
from .prompt import (
    SystemPrompt,
    HumanPrompt
)


class PromtFactory(BaseFactory):

    def get_bean(self, param: dict) -> BaseComponent:
        component_type = param["component_type"]
        if "system" == component_type:
            return SystemPrompt(param["system_prompt"])
        elif "human" == component_type:
            return HumanPrompt(param["human_message"])
        else:
            raise Exception(f"Unimplemented prompt component_type :{component_type}")