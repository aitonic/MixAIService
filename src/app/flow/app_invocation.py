from typing import TypeVar

from fastapi import APIRouter

from src.app.flow.flow_invocation import resolve_agent_config
from src.utils.response import ResponseUtil

from ..vo.request import RunData, RunParameter
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
    """Run application with configured agents.

    Args:
        req (RunParameter): Request parameters containing app configuration and data.

    Returns:
        str: Result from the final agent execution.

    Raises:
        ValueError: If no agents are configured or if execution fails.

    """
    # Group agents
    agents: dict[int, list[AgentInfo]] = arrange_agent(req)
    
    # Check if agents exist
    if not agents:
        raise ValueError(f"No agents configured for app: {req.app_no}")

    # Execute agents in order
    params = req.data.model_dump()
    orders = sorted(agents.keys())
    
    if not orders:
        raise ValueError(f"No execution orders defined for app: {req.app_no}")

    final_order = orders[-1]
    result = None

    for order in orders:
        value = agents.get(order)
        for v in value:
            new_req = req.model_copy(update={"app_no": v.agent_name})
            data_dict = new_req.data.model_dump()
            data_dict.update(params)
            new_req.data = RunData(**data_dict)
            result = resolve_agent_config(new_req)
            
            if v.result_name:
                # Pass the execution result as a parameter
                params[v.result_name] = result

    # Ensure we always return a result
    if result is None:
        raise ValueError(f"No result produced from agent execution for app: {req.app_no}")
        
    return result

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

