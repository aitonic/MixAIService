# main.py
import os
import sys
import uvicorn
import time
import yaml
from fastapi import Request, FastAPI, Query
from starlette.types import ASGIApp
from starlette.responses import StreamingResponse
import threading
import logging as logger
import src.CreateApp as CreateApp
# app = FastAPI(title='simple-ai', description='简易ai的组件服务')
app = CreateApp.App.createApp()

def on_start_up():
    # 加载组件
    from src.app.core.business_logic import load_classes_from_components, load_config
    app.components_data = load_classes_from_components()

    # 加载app配置
    app.app_config = load_config()

if __name__ == '__main__':
    try:
        logger.info("开始启动服务======")
        threading.Thread(target=on_start_up).start()
        uvicorn.run(app, host='0.0.0.0', port=8899)
    except Exception as e:
        logger.exception("server start error:{}".format(e))