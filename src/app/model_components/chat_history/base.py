from abc import ABC, abstractmethod

from ..base_component import BaseComponent
from .dto import MessageInfo, MessageListParameter


class AbsMemory(ABC, BaseComponent):
    @abstractmethod
    def save_message(self, message: MessageInfo) -> str:
        """Save or update message
        
        message: The message to be saved
        return: The corresponding id of the message
        """
        pass

    @abstractmethod
    def list_message(self, parameter: MessageListParameter) -> list[MessageInfo]:
        """Query message list
        
        parameter: Query parameters
        return: Message records queried based on conditions
        """
        pass
