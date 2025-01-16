from typing import Optional
from pydantic import BaseModel, Field

class AgentInfo(BaseModel):
    agent_name: str = Field(description="agent_config中的agent名字")
    run_order: int|None = Field(description="执行顺序,根据数值从小到大排序，同样的值，一起执行")
    result_name: str|None = Field(description="agent执行结果，作为下一个agent入参时候的名称。只有最终输出可以不必指定")

class AppConfig(BaseModel):
    agents: list[AgentInfo]
    order_configs: dict[int, list[AgentInfo]] = Field(default_factory=dict)

    def __get_order_list(self) -> dict[int, list[AgentInfo]]:
        """
        Get a dictionary of agent information grouped by execution order

        Returns:
            dict[int, list[AgentInfo]]:
                Key is the execution order value, value is the list of agent information for that order
                The returned dictionary will be sorted from smallest to largest by execution order
        """
        order_dict = {}
        for agent in self.agents:
            # 如果 run_order 为 None，则默认为 999
            order = agent.run_order if agent.run_order is not None else 999
            if order not in order_dict:
                order_dict[order] = []
            order_dict[order].append(agent)
        return dict(sorted(order_dict.items()))

    def __init__(self, agents: list[AgentInfo]):
        # print(data)
        super().__init__(agents = agents)  # 调用 Pydantic 的 __init__ 方法
        # self.agents = agents
        self.order_configs = self.__get_order_list()  # 初始化 order_configs