from fastapi import FastAPI, Request 
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback
# from config import initialConfig, get_config_value, DbEngineFactory as dbEngineFactory
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
# from log_common import logger
import logging as logger


def is_json_type(request: Request):
    if 'content-type' in request.headers and 'json' in request.headers.get('content-type'):
        return True
    
    if 'Content-Type' in request.headers and 'json' in request.headers.get('Content-Type'):
        return True
    
    return False


class HttpMiddleware(BaseHTTPMiddleware):  
    async def dispatch(self, request: Request, call_next):  
        start_time = time.time()
    
        logger.info(f'请求头信息:{request.headers}')
        
        # 做请求限流
        # from util import request_util
        # key = request.headers.get('x-real-ip')
        # if not key:
        #     key = request.headers.get('host')
            
        # reachLimit = request_util.time_limit(key)
        # if not reachLimit:
        #     raise RequestLimitException('近一分钟内请求次数超限（不得超过180次/分）')
        
        # 做日志
        if request.method == 'POST' and is_json_type(request):
            request_body = await request.json()
            logger.info(f'接收到请求：{request.url.path}, 开始时间：{start_time}, 请求体：{request_body}')
        else:
            logger.info(f'接收到请求：{request.url.path}, 开始时间：{start_time}')
        # 生成traceId
        # from log_common import logger, MthThreadLocal as mthThreadLocal
        # mthThreadLocal.generateTraceId()
        # request.state.traceId = mthThreadLocal.getTraceId()
        
        response = await call_next(request)
        # 检查响应是否为流式响应  
        if not isinstance(response, StreamingResponse):  
            # 读取响应体内容  
            body = await response.body()  
            # 转换回字符串，假设响应体是字节串  
            body_str = body.decode("utf-8") if body else ""  
            # 记录响应信息  
            logger.info(f"ai-app-service服务最终响应信息response:{body_str}")

        end_time = time.time()
        process_time = end_time - start_time
        logger.info(f'请求：{request.url.path}, 结束时间：{end_time}, 耗时：{process_time}')
        logger.info(response.raw_headers)
        # mthThreadLocal.setTraceId("")
        # request.state.traceId = ""
        return response
        
class App:
    app: FastAPI = None

    def createApp():
        if App.app:
            return App.app
        logger.info(f"开始创建服务=======")
        app = FastAPI(app_dir='main.py', title ='ai组件', description = 'ai组件服务')

        try:
            # 数据库
            # dbEngineFactory.init_db_engine(initialConfig.dbConfig, get_config_value('database.sql_echo', False))
            
            # 添加拦截器
            # app.add_middleware(RequestLoggingMiddleware)
            # app.add_event_handler
            # from handler.global_handler import (
            #     validation_exception_handler,
            #     max_exception_handler
            # )
            # app.add_exception_handler(RequestValidationError, validation_exception_handler)
            # app.add_exception_handler(Exception, max_exception_handler)
            # app.add_event_handler('startup', on_start_up(app))

            # 注册蓝图
            __register_routers__(app)  # 应用模板
            
            app.add_middleware(HttpMiddleware)
            
            # 导入nacos注册
            # import nacos_common
           
        except Exception as e:
            logger.error(f"启动报错，错误信息：{traceback.format_exc()}")

        # langchain 在dev环境开启debug
        logger.info(f'注册的url列表：{app.routes}')
        App.app = app
        return app

    def get_app():
        return App.app


def __register_routers__(app: FastAPI):
    # 引用Controlls里面的蓝图并注册

    # 应用模板
    from src.app.flow.flow_invocation import run_crtl
    app.include_router(run_crtl)