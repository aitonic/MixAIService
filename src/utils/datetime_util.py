from datetime import datetime


def get_current_timestamp() -> float:
    """获取当前时间的毫秒级时间戳。

    Returns:
        float: 当前时间的毫秒级时间戳。

    """
    return datetime.now().timestamp() * 1000
