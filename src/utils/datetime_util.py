from datetime import datetime


def get_current_timestamp():
    return datetime.now().timestamp() * 1000
