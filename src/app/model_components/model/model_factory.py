from typing import Any

from ..base_component import BaseFactory
from .dto import BaseLLMParameter
from src.app.model_components.base_component import BaseComponent
from .openai_style import (
    OpenAiStyleModel,
    OpenAiStyleLLMParameter
)
from .mix import (
    Mix,
    MixLLMParameter
)
from .embedding import OpenAiStyleEmbeddings


class ModelFactory(BaseFactory):

    def get_bean(self, param: dict) -> BaseComponent:
        component_type = param["component_type"]
        if "openai" == component_type:
            return OpenAiStyleModel(OpenAiStyleLLMParameter(**param["parameter"]))
        elif "mix" == component_type:
            return Mix(MixLLMParameter(**param["parameter"]))
        elif "openai_embedding" == component_type:
            return OpenAiStyleEmbeddings(BaseLLMParameter(**param["parameter"]))
        else:
            raise Exception(f"Unimplemented model component_type :{component_type}")