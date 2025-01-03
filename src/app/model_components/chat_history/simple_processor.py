from typing import List
from src.utils import (
    identifier_util, 
    datetime_util
)

from .base import AbsMemory
from .dto import (
    MessageInfo,
    MessageListParameter
)

# 所有使用本地内存的记忆
# {用户：{id:消息}}
memories:dict[str,dict[str:MessageInfo]] = {}

class DbMemory(AbsMemory):
    '''
        存储在DB中的记忆
        关系型数据库
        redis等非关系型数据库
    '''
    
    def __init__(self):
        # 初始化引擎
        pass

    def save_message(self, message:MessageInfo) -> str:
        '''
            保存或者更新消息
            message: 要保存的消息
            return: 该消息对应的id
        '''
        pass
        

    def list_message(self, parameter:MessageListParameter) -> List[MessageInfo]:
        '''
            查询消息列表
            parameter: 查询参数
            return: 根据条件查询到的消息记录
        '''
        pass


# 所有使用本地内存的记忆
# {用户：{id:消息}}
memories:dict[str,dict[str,MessageInfo]] = {}

class LocalMemory(AbsMemory):
    '''
        基础记忆
        使用本地内存实现
    '''
    
    
    def __init__(self):
        # 初始化引擎
        self.memories = memories

    def save_message(self, message:MessageInfo) -> str:
        '''
            保存或者更新消息
            message: 要保存的消息
            return: 该消息对应的id
        '''
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
                message_in_memory.system_message = message.system_message if message.system_message else message_in_memory.system_message
                message_in_memory.user_message = message.user_message if message.user_message else message_in_memory.user_message
                message_in_memory.assistant_message = message.assistant_message if message.assistant_message else message_in_memory.assistant_message
        return message.id
        

    def list_message(self, parameter:MessageListParameter) -> List[MessageInfo]:
        '''
            查询消息列表
            parameter: 查询参数
            return: 根据条件查询到的消息记录
        '''
        user_memory = self.memories.get(parameter.api_key, {})
        if not user_memory:
            return []
        
        messages = [mem for mem in list(user_memory.values()) if mem.created > parameter.created]
        messages.sort(key=lambda x: x.created, reverse=parameter.desc)
        return messages[:parameter.limit]
        