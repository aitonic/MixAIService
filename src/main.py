# main.py
import os
import sys
import threading

import uvicorn
from dotenv import load_dotenv

from src.create_app import create_app
from src.utils.logger import logger

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
env_path = os.path.join(project_root, "config", ".env")

load_dotenv(dotenv_path=env_path)

# app = FastAPI(title='simple-ai', description='简易ai的组件服务')
app = create_app()


if __name__ == "__main__":
    try:
        logger.info("开始启动服务======")
        
        host = os.getenv("SERVER_HOST", "127.0.0.1")
        port = int(os.getenv("SERVER_PORT", "8899"))
       
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        logger.exception(f"server start error:{e}")
