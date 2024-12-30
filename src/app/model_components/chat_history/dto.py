from pydantic import BaseModel, Field
import os
from typing import Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

class MessageInfo(BaseModel):
    '''保存的消息'''
    # 消息id
    id:Optional[str] = Field(None)
    # 用户身份识别,比如api_key
    user_id:str
    system_message:Optional[str] = Field(None)
    user_message:Optional[str] = Field(None)
    assistant_message:Optional[str] = Field(None)
    # 创建时间
    created:Optional[float] = Field(0)

class MessageListParameter(BaseModel):
    '''查询消息列表的参数'''
    # 用户身份识别
    api_key:str
    # 取出的条数
    limit:int = 3
    # 倒序，取最近的数据
    desc:bool = True
    # 开始时间
    created:float = 0