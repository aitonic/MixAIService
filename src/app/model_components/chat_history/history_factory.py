from ..base_component import (
    BaseFactory, 
    BaseComponent
)
from .simple_memory import (
    LocalMemory, 
    DbMemory
)


class MemoryFactory(BaseFactory):

    def get_bean(self, param: dict) -> BaseComponent:
        component_type = param["component_type"]
        if "local" == component_type:
            return LocalMemory()
        elif "db" == component_type:
            return DbMemory()
        else:
            raise Exception(f"Unimplemented memory component_type :{component_type}")