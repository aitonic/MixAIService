# Response
from datetime import datetime
from decimal import Decimal

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.utils.logger import logger

# def convert_value(obj: Any) -> Any:
#     if isinstance(obj, BaseModel):
#         # 对于 Pydantic 模型，遍历其字段并递归处理值
#         return obj.model_copy(
#             update={k: convert_value(v) for k, v in obj.model_dump().items()}
#         )
#     elif isinstance(obj, dict):
#         # 对于字典，递归处理值
#         return {k: convert_value(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         # 对于列表，递归处理每个元素
#         return [convert_value(item) for item in obj]
#     elif isinstance(obj, datetime):
#         # 对于 datetime 对象，直接转换为 ISO 格式
#         # return obj.isoformat()
#         return obj.strftime("%Y-%m-%d %H:%M:%S")
#     elif isinstance(obj, Decimal):
#         # 对于 datetime 对象，直接转换为 ISO 格式
#         # return obj.isoformat()
#         return str(obj)
#     else:
#         # 对于其他类型，直接返回对象本身
#         return obj

def convert_value(
    obj: BaseModel | dict[str, "ValueType"] | list["ValueType"] | datetime | Decimal | str | int | float | None
) -> dict[str, "ValueType"] | list["ValueType"] | str | int | float | None:
    """Recursively convert object values.

    Args:
        obj: Input object, which can be Pydantic model, dict, list, datetime, Decimal or other types.

    Returns:
        Union[Dict, List, str, int, float, None]: Converted object.

    """
    if isinstance(obj, BaseModel):
        # For Pydantic model, recursively process its fields
        return obj.model_copy(
            update={k: convert_value(v) for k, v in obj.model_dump().items()}
        )
    elif isinstance(obj, dict):
        # For dictionary, recursively process values
        return {k: convert_value(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # For list, recursively process each element
        return [convert_value(item) for item in obj]
    elif isinstance(obj, datetime):
        # For datetime object, convert to ISO format
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, Decimal):
        # For Decimal object, convert to string
        return str(obj)
    else:
        # For other types, return the object itself
        return obj

# Type alias for recursive reference
ValueType = BaseModel | dict[str, "ValueType"] | list["ValueType"] | datetime | Decimal | str | int | float | None

# def convert_obj(obj: Any) -> Any:
#     """转换对象为指定格式。

#     Args:
#         obj (Any): 输入的对象，支持任意类型。

#     Returns:
#         Any: 转换后的对象。

#     """
#     obi = (
#         convert_value(obj)
#         if isinstance(obj, BaseModel)
#         else (
#             obj if not isinstance(obj, datetime) else obj.strftime("%Y-%m-%d %H:%M:%S")
#         )
#     )
#     # obi = convert_value(obj) if isinstance(obj, BaseModel) else obj

#     if isinstance(obi, list):
#         return [i.model_dump() if isinstance(i, BaseModel) else i for i in obi]
#     return obi.model_dump() if isinstance(obi, BaseModel) else obi


def convert_obj(
    obj: BaseModel | list[BaseModel | dict | str | int | float] | datetime | str | int | float | None
) -> dict | list[dict | str | int | float] | str | int | float | None:
    """Convert object to specified format.

    Args:
        obj (Union[BaseModel, List, datetime, str, int, float, None]): Input object, supports Pydantic model, list, datetime or other types.

    Returns:
        Union[Dict, List, str, int, float, None]: Converted object.

    """
    obi = (
        convert_value(obj)
        if isinstance(obj, BaseModel)
        else (
            obj if not isinstance(obj, datetime) else obj.strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    if isinstance(obi, list):
        return [i.model_dump() if isinstance(i, BaseModel) else i for i in obi]
    elif isinstance(obi, dict):
        for key, value in obi.items():
            obi[key] = convert_obj(value)
        
        return obi
    return obi.model_dump() if isinstance(obi, BaseModel) else obi


class ResponseUtil:
    @staticmethod
    def success(result: dict | str | None = None, code: int = 200000) -> dict:
        # 对象转换
        result = convert_obj(result)
        logger.info(f"正常响应信息：{result}")
        return JSONResponse(
            content={"code": code, "message": "success", "result": result}
        )

    @staticmethod
    def fail(result: dict | str | None = None, msg: str = "fail", code: int = 500000) -> dict:
        """返回一个失败响应。

        Args:
            result (Optional[Union[Dict, str]]): 结果对象或错误信息，默认为 None。
            msg (str): 响应的消息内容，默认为 "fail"。
            code (int): 错误代码，默认为 500000。

        Returns:
            Dict: 包含错误信息的响应字典。

        """
        result = result.model_dump() if isinstance(result, BaseModel) else result
        logger.info(f"异常响应信息：{result}")
        return JSONResponse(content={"code": code, "message": msg, "result": result})
