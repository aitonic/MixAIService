import time
import traceback
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from src.utils.exceptions import AIBaseError
from src.utils.logger import logger
from src.utils.response import ResponseUtil



def exception_handler(request: Request, e: Exception) -> Response:
    """Handle exceptions that occur during request processing.

    Args:
        request (Request): The incoming HTTP request object
        e (Exception): The exception that occurred during processing

    Returns:
        Response: A structured JSON response containing error details

    This function performs the following tasks:
    1. Logs the error details including stack trace
    2. Returns a structured JSON response to the client
    3. Includes specific error details if the exception is a validation error
    4. Provides a generic error message for other types of exceptions

    """
    try:
        logger.error(f"serverErr error: {traceback.format_exc()}")

        if isinstance(e, AIBaseError):
            return ResponseUtil.fail(msg=e.message, status_code=e.status_code)

        if isinstance(e, ValidationError):
            logger.error(f"{e.errors()}")
            return ResponseUtil.fail(msg=e.errors())

        message = e.args[0]
        return ResponseUtil.fail(msg=message)
    except Exception:
        logger.error(f"serverErr error: {traceback.format_exc()}")
        return ResponseUtil.fail(msg='fail', result='系统异常，请联系管理员')
    
def is_json_type(request: Request) -> bool:
    """Check if the request header contains JSON Content-Type.

    Args:
        request (Request): HTTP request object.

    Returns:
        bool: Returns True if Content-Type contains 'json', otherwise False.

    """
    return (
        "content-type" in request.headers and "json" in request.headers.get("content-type")
    ) or (
        "Content-Type" in request.headers and "json" in request.headers.get("Content-Type")
    )

class HttpMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()

        logger.info(f"请求头信息:{request.headers}")

        # 做日志
        if request.method == "POST" and is_json_type(request):
            request_body = await request.json()
            logger.info(
                f"接收到请求：{request.url.path}, 开始时间：{start_time}, 请求体：{request_body}"
            )
        else:
            logger.info(f"接收到请求：{request.url.path}, 开始时间：{start_time}")
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
        logger.info(
            f"请求：{request.url.path}, 结束时间：{end_time}, 耗时：{process_time}"
        )
        logger.info(response.raw_headers)
        # mthThreadLocal.setTraceId("")
        # request.state.traceId = ""
        return response


def create_app()-> FastAPI:
    """获取 App 的应用实例。

    Returns:
        Any: App 的应用实例。

    """
    logger.info("开始创建服务=======")
    app = FastAPI(app_dir="main.py", title="ai组件", description="ai组件服务")

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
        app.add_exception_handler(Exception, exception_handler)

        # 注册蓝图
        _register_routers(app)  # 应用模板

        app.add_middleware(HttpMiddleware)

        # 启动后事件
        _on_start_up(app)

    except Exception:
        # Log error message when startup fails
        logger.error(f"Startup error, error info: {traceback.format_exc()}")

    # Log registered URL list
    logger.info(f"Registered URL list: {app.routes}")
    return app


def _register_routers(app: FastAPI) -> None:
    # 引用Controlls里面的蓝图并注册

    # 应用模板
    from src.app.flow.flow_invocation import agent_crtl
    app.include_router(agent_crtl) 
    
    from src.app.flow.app_invocation import app_crtl
    app.include_router(app_crtl)



def _on_start_up(app:FastAPI) -> None:
    # 加载组件
    from src.app.core.business_logic import (
        load_agent_config,
        load_app_config,
        load_classes_from_components,
        load_factories,
    )

    app.components_data = load_classes_from_components()

    # 加载app配置
    app.app_config = load_app_config()

    # 加载agent配置
    app.agent_config = load_agent_config()

    # 加载所有的factory
    app.factory = load_factories()
