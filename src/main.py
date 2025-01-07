# main.py
import logging as logger
import os
import sys
import threading

import uvicorn
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
import src.CreateApp as CreateApp
# app = FastAPI(title='simple-ai', description='简易ai的组件服务')
app = CreateApp.App.createApp()


def on_start_up():
    # 加载组件
    from src.app.core.business_logic import (
        load_agent_config,
        load_app_config,
        load_classes_from_components,
    )

    app.components_data = load_classes_from_components()

    # 加载app配置
    app.app_config = load_app_config()

    # 加载agent配置
    app.agent_config = load_agent_config()


if __name__ == "__main__":
    try:
        logger.info("开始启动服务======")
        threading.Thread(target=on_start_up).start()
        uvicorn.run(app, host="0.0.0.0", port=8899)
    except Exception as e:
        logger.exception(f"server start error:{e}")
