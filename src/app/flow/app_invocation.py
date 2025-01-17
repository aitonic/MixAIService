from collections.abc import Iterator
from typing import TypeVar

from fastapi import APIRouter

from src.app.model_components.base_component import BaseFactory
from src.utils.logger import logger
from src.utils.response import ResponseUtil
from src.app.flow.flow_invocation import resolve_agent_config


from ..vo.request import RunParameter
from .dto.app_dto import (
    AgentInfo, 
    AppConfig
) 

app_crtl = APIRouter()

T = TypeVar("T")


@app_crtl.post("/simple-ai/run_app")
def run_app_with_config(req: RunParameter) -> str:
    
    datas = req.data
    req.data.text = datas.query
    req.data.input = datas.query
    req.data.query_text = datas.query
    
 
    return ResponseUtil.success(run_app(req))

def run_app(req: RunParameter) -> str:
    # Group agents
    agents:dict[int, list[AgentInfo]] = arrange_agent(req)

    # Execute agents in order
    params = req.data.model_dump()
    # Get the maximum run_order, which is the final execution of the flow
    orders = list(agents.keys())
    orders.sort()
    final_order = orders[-1]
    for order in orders:
        value = agents.get(order)
        for v in value:
            new_req = req.model_copy(update={"app_no":v.agent_name})
            result = resolve_agent_config(new_req)
            if order == final_order:
                return result
            
            if v.result_name:
                # Pass the execution result as a parameter
                params[v.result_name] = result
            

def arrange_agent(req: RunParameter) -> dict[int, list[AgentInfo]]:
    from src.main import app
    app_configs = app.app_config.get(req.app_no)
    if not app_configs:
        raise Exception(f"app_no not exist in app configs:{req.app_no}")
    
    # Get application configuration
    # app_config = AppConfig(agents = app_configs)
    app_config = AppConfig(agents = [AgentInfo(**config) for config in app_configs])
    print(app_config)
    return app_config.order_configs

