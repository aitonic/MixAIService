from typing import TypeVar

from fastapi import APIRouter

from src.app.flow.flow_invocation import resolve_agent_config
from src.utils.response import ResponseUtil

from ..vo.request import RunParameter
from .dto.app_dto import AgentInfo, AppConfig

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
    # agent分组构建
    agents:dict[int, list[AgentInfo]] = arrange_agent(req)

    # 根据顺序执行agent
    params = req.data.model_dump()
    # 取出最大的run_order，也就是flow的终极执行
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
                # 将执行结果，作为参数继续传递
                params[v.result_name] = result
            

def arrange_agent(req: RunParameter) -> dict[int, list[AgentInfo]]:
    from src.main import app
    app_configs = app.app_config.get(req.app_no)
    if not app_configs:
        raise Exception(f"app_no not exist in app configs:{req.app_no}")
    
    # 取出应用配置
    # app_config = AppConfig(agents = app_configs)
    app_config = AppConfig(agents = [AgentInfo(**config) for config in app_configs])
    print(app_config)
    return app_config.order_configs


