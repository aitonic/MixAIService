from datetime import datetime


def get_current_timestamp() -> float:
    """Get the current timestamp in milliseconds.

    Returns:
        float: The current timestamp in milliseconds.

    """
    return datetime.now().timestamp() * 1000
