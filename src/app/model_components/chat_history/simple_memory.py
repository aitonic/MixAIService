from src.utils import datetime_util, identifier_util

from .base import AbsMemory
from .dto import MessageInfo, MessageListParameter

# 所有使用本地内存的记忆
# {用户：{id:消息}}
memories: dict[str, dict[str:MessageInfo]] = {}


class DbMemory(AbsMemory):
    """Memory stored in database
    
    Relational database
    Non-relational database like Redis
    """

    def __init__(self) -> None:
        # 初始化引擎
        raise Exception("Unimplemented memory: DB Memory")

    def save_message(self, message: MessageInfo) -> str:
        """Save or update message
        
        message: The message to be saved
        return: The corresponding id of the message
        """
        pass

    def list_message(self, parameter: MessageListParameter) -> list[MessageInfo]:
        """Query message list
        
        parameter: Query parameters
        return: Message records queried based on conditions
        """
        pass


# 所有使用本地内存的记忆
# {用户：{id:消息}}
memories: dict[str, dict[str, MessageInfo]] = {}


class LocalMemory(AbsMemory):
    """Basic memory
    
    Implemented using local memory
    """

    def __init__(self) -> None:
        # 初始化引擎
        self.memories = memories

    def save_message(self, message: MessageInfo) -> str:
        """Save or update message
        
        message: The message to be saved
        return: The corresponding id of the message
        """
        if not message.id:
            # 新增保存
            id = identifier_util.generate_by_uuid()
            message.id = id
            if not message.created:
                message.created = datetime_util.get_current_timestamp()
            user_memory = self.memories.get(message.user_id, {})
            user_memory[message.id] = message
            self.memories[message.user_id] = user_memory
        else:
            # 更新
            message_in_memory = self.memories.get(message.user_id, {}).get(message.id)
            if message_in_memory:
                message_in_memory.system_message = (
                    message.system_message
                    if message.system_message
                    else message_in_memory.system_message
                )
                message_in_memory.user_message = (
                    message.user_message
                    if message.user_message
                    else message_in_memory.user_message
                )
                message_in_memory.assistant_message = (
                    message.assistant_message
                    if message.assistant_message
                    else message_in_memory.assistant_message
                )
        return message.id

    def list_message(self, parameter: MessageListParameter) -> list[MessageInfo]:
        """Query message list
        
        parameter: Query parameters
        return: Message records queried based on conditions
        """
        user_memory = self.memories.get(parameter.api_key, {})
        if not user_memory:
            return []

        messages = [
            mem for mem in list(user_memory.values()) if mem.created > parameter.created
        ]
        messages.sort(key=lambda x: x.created, reverse=parameter.desc)
        return messages[: parameter.limit]
