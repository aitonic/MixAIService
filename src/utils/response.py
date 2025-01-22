# Response
from datetime import datetime
from decimal import Decimal

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.utils.logger import logger


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
        """Return a success response with the given result.

        Args:
            result (Optional[Union[Dict, str]]): Result object or success message, defaults to None.
            code (int): Success code, defaults to 200000.

        Returns:
            Dict: Response dictionary containing success information.

        """
        result = convert_obj(result)
        logger.info(f"正常响应信息：{result}")
        return JSONResponse(
            content={"code": code, "message": "success", "result": result}
        )

    @staticmethod
    def fail(result: dict | str | None = None, msg: str = "fail", code: int = 500000) -> dict:
        """Return a failure response.

        Args:
            result (Optional[Union[Dict, str]]): Result object or error message, defaults to None.
            msg (str): Response message content, defaults to "fail".
            code (int): Error code, defaults to 500000.

        Returns:
            Dict: Response dictionary containing error information.

        """
        result = result.model_dump() if isinstance(result, BaseModel) else result
        logger.info(f"异常响应信息：{result}")
        return JSONResponse(content={"code": code, "message": msg, "result": result})
