# 根据value内容进行enum的获取
def get_enum_by_value(enum_class, value):
    for member in enum_class:
        if member.value == value:
            return member
    return None