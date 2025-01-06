import hashlib
import uuid
from datetime import datetime

"""
    唯一id生成器
"""


def generate_by_sha256(seed_string: str = None) -> str:
    """使用SHA256哈希算法，生成结果64位"""
    if not seed_string or len(seed_string) == 0:
        # 如果种子是空，则使用当前时间作为种子
        seed_string = str(datetime.now().timestamp())
    sha_signature = hashlib.sha256(seed_string.encode()).hexdigest()
    return sha_signature


# 使用uuid生成唯一id
def generate_by_uuid(name: str = None) -> str:
    if not name or len(name) == 0:
        # 如果种子是空，则使用当前时间作为种子
        return uuid.uuid4().__str__().replace("-", "")
    # 生成uuid5
    return uuid.uuid5(uuid.NAMESPACE_X500, name).__str__().replace("-", "")


# if __name__ == '__main__':
#     print(generate_by_uuid())
