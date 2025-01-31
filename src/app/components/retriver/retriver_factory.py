from ..base_component import BaseComponent, BaseFactory
from .vector_retriver import VectorRetriver


class RetriverFactory(BaseFactory):
    """Retrieve information.
    Search for matching content lists from specified sources based on input information
    and other specified parameters (to be handled by respective implementations).
    """

    def get_bean(self, param: dict) -> BaseComponent:
        
        return VectorRetriver(param["vector_store"])
