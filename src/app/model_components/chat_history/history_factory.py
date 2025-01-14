from ..base_component import (
    BaseFactory, 
    BaseComponent
)


class MemoryFactory(BaseFactory):

    def get_bean(self, param: dict) -> BaseComponent:
        return super().get_bean(param)