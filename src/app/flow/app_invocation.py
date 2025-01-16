from collections.abc import Iterator
from typing import TypeVar

from fastapi import APIRouter

from src.app.model_components.base_component import BaseFactory
from src.utils.logger import logger
from src.utils.response import ResponseUtil

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
    
 
    return ResponseUtil.success(arrange_agent(req))

def arrange_agent(req: RunParameter):
    from src.main import app
    app_configs = app.app_config.get(req.app_no)
    if not app_configs:
        raise Exception(f"app_no not exist in app configs:{req.app_no}")
    
    # 取出应用配置
    # app_config = AppConfig(agents = app_configs)
    app_config = AppConfig(agents = [AgentInfo(**config) for config in app_configs])
    print(app_config)
    return app_config.order_configs


