class BaseComponent:
    """
    基础组件。
    所有的组件，都需要继承自这个组件。
    """

    def as_parameter(self) -> "BaseComponent":
        # 该方法用于将当前组件作为参数返回，方便其他组件使用。
        # 通过调用此方法，用户可以获取到当前组件的实例。
        return self