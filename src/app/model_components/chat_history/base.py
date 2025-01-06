from abc import ABC, abstractmethod

from .dto import MessageInfo, MessageListParameter


class AbsMemory(ABC):
    @abstractmethod
    def save_message(self, message: MessageInfo) -> str:
        """保存或者更新消息
        message: 要保存的消息
        return: 该消息对应的id
        """
        pass

    @abstractmethod
    def list_message(self, parameter: MessageListParameter) -> list[MessageInfo]:
        """查询消息列表
        parameter: 查询参数
        return: 根据条件查询到的消息记录
        """
        pass
