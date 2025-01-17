from ..base_component import (
    BaseFactory,
    BaseComponent
)
from .dto import BaseLLMParameter
from .embedding import OpenAiStyleEmbeddings
from .mix import (
    Mix,
    MixLLMParameter
)
from .openai_style import (
    OpenAiStyleModel,
    OpenAiStyleLLMParameter
)


class ModelFactory(BaseFactory):

    def __init__(self):
        self._component_map = {
            "openai": lambda p: OpenAiStyleModel(OpenAiStyleLLMParameter(**p)),
            "mix": lambda p: Mix(MixLLMParameter(**p)),
            "openai_embedding": lambda p: OpenAiStyleEmbeddings(BaseLLMParameter(**p))
        }
    
    # def get_bean(self, param: dict) -> BaseComponent:
    #     component_type = param["component_type"]
    #     if "openai" == component_type:
    #         return OpenAiStyleModel(OpenAiStyleLLMParameter(**param["parameter"]))
    #     elif "mix" == component_type:
    #         return Mix(MixLLMParameter(**param["parameter"]))
    #     elif "openai_embedding" == component_type:
    #         return OpenAiStyleEmbeddings(BaseLLMParameter(**param["parameter"]))
    #     else:
    #         raise Exception(f"Unimplemented model component_type :{component_type}")
    
    def get_bean(self, param: dict) -> BaseComponent:
        component_type = param["component_type"]
        component_creator = self._component_map.get(component_type)
        
        if not component_creator:
            raise Exception(f"Unimplemented model component_type: {component_type}")
            
        return component_creator(param["parameter"])