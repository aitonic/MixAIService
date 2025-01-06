import logging as logger
from datetime import datetime
from decimal import Decimal

from fastapi.responses import JSONResponse
from pydantic import BaseModel


def convert_value(obj):
    if isinstance(obj, BaseModel):
        # 对于 Pydantic 模型，遍历其字段并递归处理值
        return obj.model_copy(
            update={k: convert_value(v) for k, v in obj.model_dump().items()}
        )
    elif isinstance(obj, dict):
        # 对于字典，递归处理值
        return {k: convert_value(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # 对于列表，递归处理每个元素
        return [convert_value(item) for item in obj]
    elif isinstance(obj, datetime):
        # 对于 datetime 对象，直接转换为 ISO 格式
        # return obj.isoformat()
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, Decimal):
        # 对于 datetime 对象，直接转换为 ISO 格式
        # return obj.isoformat()
        return str(obj)
    else:
        # 对于其他类型，直接返回对象本身
        return obj


def convert_obj(obj):
    obi = (
        convert_value(obj)
        if isinstance(obj, BaseModel)
        else (
            obj if not isinstance(obj, datetime) else obj.strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    # obi = convert_value(obj) if isinstance(obj, BaseModel) else obj

    if isinstance(obi, list):
        return [i.model_dump() if isinstance(i, BaseModel) else i for i in obi]
    return obi.model_dump() if isinstance(obi, BaseModel) else obi


class ResponseUtil:
    @staticmethod
    def success(result=None, code: int = 200000):
        # 对象转换
        result = convert_obj(result)
        logger.info(f"正常响应信息：{result}")
        return JSONResponse(
            content={"code": code, "message": "success", "result": result}
        )

    @staticmethod
    def fail(result=None, msg="fail", code: int = 500000):
        result = result.model_dump() if isinstance(result, BaseModel) else result
        logger.info(f"异常响应信息：{result}")
        return JSONResponse(content={"code": code, "message": msg, "result": result})
