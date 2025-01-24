from ..base_component import BaseComponent, BaseFactory
from .simple_memory import DbMemory, LocalMemory


class MemoryFactory(BaseFactory):

    def get_bean(self, param: dict) -> BaseComponent:
        component_type = param["component_type"]
        if component_type == "local":
            return LocalMemory()
        elif component_type == "db":
            return DbMemory()
        else:
            raise Exception(f"Unimplemented memory component_type :{component_type}")
